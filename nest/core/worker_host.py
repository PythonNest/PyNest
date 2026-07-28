from __future__ import annotations

import asyncio
import inspect
import logging
import math
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from nest.common.background_worker import (
    BackgroundWorker,
    RestartPolicy,
    WorkerState,
    WorkerStatus,
)
from nest.core.pynest_container import PyNestContainer


@dataclass
class _WorkerRuntime:
    worker: BackgroundWorker
    name: str
    restart: RestartPolicy
    restart_backoff: float
    restart_backoff_max: float
    state: WorkerState = WorkerState.STOPPED
    restarts: int = 0
    last_error: Optional[str] = None
    task: Optional[asyncio.Task[None]] = None
    start_hook_called: bool = False
    stop_hook_called: bool = False


class WorkerHost:
    """Supervises all background worker providers for one application."""

    def __init__(
        self,
        workers: Iterable[BackgroundWorker],
        *,
        grace_timeout: float = 10.0,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._grace_timeout = self._validate_number(grace_timeout, "grace_timeout")
        self._logger = logger or logging.getLogger("pynest.workers")
        self._runtimes = self._build_runtimes(workers)
        self._running = False
        self._stop_task: Optional[asyncio.Task[None]] = None

    @classmethod
    def discover(
        cls,
        container: PyNestContainer,
        *,
        grace_timeout: float = 10.0,
    ) -> "WorkerHost":
        """Create a host from dependency-injected worker providers."""
        return cls(
            container.get_instances_of(BackgroundWorker),
            grace_timeout=grace_timeout,
        )

    @property
    def workers(self) -> tuple[BackgroundWorker, ...]:
        return tuple(runtime.worker for runtime in self._runtimes)

    @property
    def running(self) -> bool:
        return self._running

    async def start(self) -> None:
        """Start every worker on the current event loop."""
        if self._running:
            return

        self._running = True
        self._stop_task = None
        for runtime in self._runtimes:
            runtime.worker._prepare_for_start()
            runtime.state = WorkerState.STARTING
            runtime.restarts = 0
            runtime.last_error = None
            runtime.start_hook_called = False
            runtime.stop_hook_called = False
            runtime.task = asyncio.create_task(
                self._supervise(runtime),
                name=f"pynest-worker:{runtime.name}",
            )

    async def stop(self) -> None:
        """Request cooperative shutdown, then cancel work past the deadline."""
        if self._stop_task is not None:
            await asyncio.shield(self._stop_task)
            return
        if not self._running:
            return

        self._stop_task = asyncio.create_task(
            self._stop(), name="pynest-worker-shutdown"
        )
        await asyncio.shield(self._stop_task)

    async def wait(self) -> None:
        """Wait until all currently managed workers have exited."""
        tasks = [runtime.task for runtime in self._runtimes if runtime.task is not None]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def get_status(self) -> tuple[WorkerStatus, ...]:
        """Return immutable status snapshots in discovery order."""
        return tuple(
            WorkerStatus(
                name=runtime.name,
                state=runtime.state,
                restarts=runtime.restarts,
                last_error=runtime.last_error,
            )
            for runtime in self._runtimes
        )

    def status(self) -> list[dict[str, object]]:
        """Return JSON-ready status dictionaries."""
        return [status.as_dict() for status in self.get_status()]

    async def _supervise(self, runtime: _WorkerRuntime) -> None:
        if runtime.worker.stopping.is_set():
            runtime.state = WorkerState.STOPPED
            return

        try:
            await self._call_hook(runtime.worker.on_start)
        except asyncio.CancelledError:
            runtime.state = WorkerState.STOPPED
            raise
        except Exception as exc:
            self._record_failure(runtime, exc, "start")
            return
        runtime.start_hook_called = True

        if runtime.worker.stopping.is_set():
            await self._run_stop_hook(runtime)
            runtime.state = WorkerState.STOPPED
            return

        while not runtime.worker.stopping.is_set():
            runtime.state = WorkerState.RUNNING
            failed = False
            try:
                await runtime.worker.run()
            except asyncio.CancelledError:
                runtime.state = (
                    WorkerState.STOPPED
                    if runtime.worker.stopping.is_set()
                    else WorkerState.FAILED
                )
                raise
            except Exception as exc:
                failed = True
                self._record_failure(runtime, exc, "run")

            if runtime.worker.stopping.is_set():
                runtime.state = WorkerState.STOPPED
                return

            should_restart = runtime.restart is RestartPolicy.ALWAYS or (
                failed and runtime.restart is RestartPolicy.ON_FAILURE
            )
            if not should_restart:
                runtime.state = WorkerState.FAILED if failed else WorkerState.COMPLETED
                return

            runtime.restarts += 1
            runtime.state = WorkerState.BACKING_OFF
            delay = min(
                runtime.restart_backoff * (2 ** min(runtime.restarts - 1, 62)),
                runtime.restart_backoff_max,
            )
            self._logger.info(
                "Restarting background worker %s in %.3f seconds",
                runtime.name,
                delay,
            )
            if not await runtime.worker.sleep(delay):
                runtime.state = WorkerState.STOPPED
                return

        runtime.state = WorkerState.STOPPED

    async def _stop(self) -> None:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + self._grace_timeout
        active_runtimes = [
            runtime
            for runtime in self._runtimes
            if runtime.task is not None and not runtime.task.done()
        ]
        hook_runtimes = [
            runtime
            for runtime in self._runtimes
            if runtime.start_hook_called and not runtime.stop_hook_called
        ]

        try:
            for runtime in active_runtimes:
                runtime.state = WorkerState.STOPPING
                runtime.worker._request_stop()

            hook_tasks = [
                asyncio.create_task(
                    self._run_stop_hook(runtime),
                    name=f"pynest-worker-stop-hook:{runtime.name}",
                )
                for runtime in hook_runtimes
            ]
            await self._wait_until_deadline(hook_tasks, deadline)

            worker_tasks = [
                runtime.task for runtime in active_runtimes if runtime.task is not None
            ]
            await self._wait_until_deadline(worker_tasks, deadline)
        finally:
            for runtime in active_runtimes:
                if runtime.state is WorkerState.STOPPING:
                    runtime.state = WorkerState.STOPPED
            self._running = False

    async def _run_stop_hook(self, runtime: _WorkerRuntime) -> None:
        if runtime.stop_hook_called:
            return
        runtime.stop_hook_called = True
        try:
            await self._call_hook(runtime.worker.on_stop)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if runtime.last_error is None:
                runtime.last_error = self._format_error(exc)
            self._logger.exception(
                "Background worker %s failed during stop", runtime.name
            )

    async def _wait_until_deadline(
        self, tasks: Iterable[asyncio.Task[Any]], deadline: float
    ) -> None:
        task_set = set(tasks)
        if not task_set:
            return

        remaining = max(0.0, deadline - asyncio.get_running_loop().time())
        _, pending = await asyncio.wait(task_set, timeout=remaining)
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)

    def _record_failure(
        self, runtime: _WorkerRuntime, exc: Exception, phase: str
    ) -> None:
        runtime.last_error = self._format_error(exc)
        runtime.state = WorkerState.FAILED
        self._logger.exception(
            "Background worker %s failed during %s", runtime.name, phase
        )

    def _build_runtimes(
        self, workers: Iterable[BackgroundWorker]
    ) -> list[_WorkerRuntime]:
        runtimes: list[_WorkerRuntime] = []
        names: set[str] = set()

        for worker in workers:
            if not isinstance(worker, BackgroundWorker):
                raise TypeError(
                    "WorkerHost only accepts BackgroundWorker instances, "
                    f"got {type(worker).__name__}"
                )
            name = self._worker_name(worker)
            if name in names:
                raise ValueError(f"Duplicate background worker name: {name!r}")
            names.add(name)

            try:
                restart = RestartPolicy(worker.restart)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid restart policy for background worker {name!r}: "
                    f"{worker.restart!r}"
                ) from exc

            restart_backoff = self._validate_number(
                worker.restart_backoff,
                f"restart_backoff for background worker {name!r}",
            )
            restart_backoff_max = self._validate_number(
                worker.restart_backoff_max,
                f"restart_backoff_max for background worker {name!r}",
            )
            if restart_backoff_max < restart_backoff:
                raise ValueError(
                    f"restart_backoff_max for background worker {name!r} "
                    "must be greater than or equal to restart_backoff"
                )

            runtimes.append(
                _WorkerRuntime(
                    worker=worker,
                    name=name,
                    restart=restart,
                    restart_backoff=restart_backoff,
                    restart_backoff_max=restart_backoff_max,
                )
            )

        return runtimes

    @staticmethod
    async def _call_hook(hook) -> None:
        result = hook()
        if inspect.isawaitable(result):
            await result

    @staticmethod
    def _worker_name(worker: BackgroundWorker) -> str:
        configured_name = worker.name
        if not isinstance(configured_name, str):
            raise ValueError("Background worker name must be a string")
        return configured_name.strip() or type(worker).__name__

    @staticmethod
    def _validate_number(value: float, name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a finite, non-negative number")
        number = float(value)
        if not math.isfinite(number) or number < 0:
            raise ValueError(f"{name} must be a finite, non-negative number")
        return number

    @staticmethod
    def _format_error(exc: BaseException) -> str:
        return f"{type(exc).__name__}: {exc}"
