from __future__ import annotations

import asyncio
import signal as signal_module
from typing import Iterable, Optional, Type

from nest.core.pynest_container import PyNestContainer
from nest.core.pynest_factory import AbstractPyNestFactory, ModuleType
from nest.core.worker_host import WorkerHost


class WorkerApplication:
    """A dependency-injection application that runs without an HTTP server."""

    def __init__(
        self,
        container: PyNestContainer,
        *,
        grace_timeout: float = 10.0,
    ) -> None:
        self.container = container
        self._worker_host = WorkerHost.discover(container, grace_timeout=grace_timeout)
        self._shutdown_requested = asyncio.Event()
        self._started = False
        self._closed = False
        self._close_task: Optional[asyncio.Task[None]] = None
        self.signal: Optional[str] = None

    @property
    def closed(self) -> bool:
        return self._closed

    def get_worker_host(self) -> WorkerHost:
        return self._worker_host

    async def start(self) -> None:
        """Initialize application lifecycle and start worker tasks."""
        if self._closed:
            raise RuntimeError("Cannot start a closed worker application")
        if self._started:
            return

        await self.container.initialize_lifecycle()
        await self._worker_host.start()
        self._started = True

    def request_shutdown(self, signal: Optional[str] = None) -> None:
        """Request shutdown without blocking a signal-handler callback."""
        if signal is not None:
            self.signal = signal
        self._shutdown_requested.set()

    async def run(self) -> None:
        """Run until all workers finish or process shutdown is requested."""
        await self.start()
        workers_done = asyncio.create_task(
            self._worker_host.wait(), name="pynest-workers-complete"
        )
        shutdown_requested = asyncio.create_task(
            self._shutdown_requested.wait(), name="pynest-workers-shutdown-request"
        )

        try:
            await asyncio.wait(
                (workers_done, shutdown_requested),
                return_when=asyncio.FIRST_COMPLETED,
            )
        finally:
            try:
                await self.close(self.signal)
            finally:
                for task in (workers_done, shutdown_requested):
                    if not task.done():
                        task.cancel()
                await asyncio.gather(
                    workers_done, shutdown_requested, return_exceptions=True
                )

    async def close(self, signal: Optional[str] = None) -> None:
        """Stop workers and run container shutdown hooks once."""
        if self._close_task is not None:
            await asyncio.shield(self._close_task)
            return
        if self._closed:
            return

        if signal is not None:
            self.signal = signal
        self._close_task = asyncio.create_task(
            self._close(), name="pynest-worker-application-close"
        )
        await asyncio.shield(self._close_task)

    async def _close(self) -> None:
        try:
            await self._worker_host.stop()
            if self._started:
                await self.container.shutdown_lifecycle(self.signal)
            self._closed = True
        finally:
            self._started = False


class WorkerAppFactory(AbstractPyNestFactory):
    """Build standalone, non-HTTP PyNest worker applications."""

    @staticmethod
    def create(
        main_module: Type[ModuleType],
        *,
        grace_timeout: float = 10.0,
        **kwargs,
    ) -> WorkerApplication:
        if kwargs:
            unexpected = ", ".join(sorted(kwargs))
            raise TypeError(f"Unexpected worker application options: {unexpected}")

        container = PyNestContainer()
        container.add_module(main_module)
        container.build()
        return WorkerApplication(container, grace_timeout=grace_timeout)


def run_workers(
    main_module: Type[ModuleType],
    *,
    grace_timeout: float = 10.0,
    signals: Optional[Iterable[signal_module.Signals]] = None,
) -> None:
    """Run a standalone worker application until completion or a signal."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        pass
    else:
        raise RuntimeError(
            "run_workers() cannot be called from a running event loop; "
            "use WorkerAppFactory.create() and await app.run() instead"
        )

    asyncio.run(
        _run_workers(
            main_module,
            grace_timeout=grace_timeout,
            signals=signals,
        )
    )


async def _run_workers(
    main_module: Type[ModuleType],
    *,
    grace_timeout: float,
    signals: Optional[Iterable[signal_module.Signals]],
) -> None:
    app = WorkerAppFactory.create(main_module, grace_timeout=grace_timeout)
    loop = asyncio.get_running_loop()
    shutdown_signals = (
        tuple(signals)
        if signals is not None
        else (signal_module.SIGTERM, signal_module.SIGINT)
    )
    previous_handlers = {
        shutdown_signal: signal_module.getsignal(shutdown_signal)
        for shutdown_signal in shutdown_signals
    }
    loop_handlers: set[signal_module.Signals] = set()

    try:
        for shutdown_signal in shutdown_signals:
            try:
                loop.add_signal_handler(
                    shutdown_signal,
                    app.request_shutdown,
                    shutdown_signal.name,
                )
                loop_handlers.add(shutdown_signal)
            except (NotImplementedError, RuntimeError):
                signal_module.signal(
                    shutdown_signal,
                    _make_signal_handler(loop, app, shutdown_signal),
                )

        await app.run()
    finally:
        for shutdown_signal, previous_handler in previous_handlers.items():
            if shutdown_signal in loop_handlers:
                loop.remove_signal_handler(shutdown_signal)
            signal_module.signal(shutdown_signal, previous_handler)


def _make_signal_handler(
    loop: asyncio.AbstractEventLoop,
    app: WorkerApplication,
    shutdown_signal: signal_module.Signals,
):
    def handler(signum, frame) -> None:
        try:
            signal_name = signal_module.Signals(signum).name
        except ValueError:
            signal_name = shutdown_signal.name
        loop.call_soon_threadsafe(app.request_shutdown, signal_name)

    return handler
