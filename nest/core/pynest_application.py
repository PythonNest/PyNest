from __future__ import annotations

import asyncio
import inspect
import signal as signal_module
from contextlib import asynccontextmanager
from typing import Any, Iterable, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from nest.common.route_resolver import RoutesResolver
from nest.core.pynest_container import PyNestContainer


class PyNestApp:
    """
    Main PyNest application. Wraps a built container and a FastAPI HTTP server.
    """

    def __init__(self, container: PyNestContainer, http_server: FastAPI) -> None:
        self.container = container
        self.http_server = http_server
        self._closed = False
        self._closing = False
        self._install_lifespan_shutdown()
        routes_resolver = RoutesResolver(self.container, self.http_server)
        routes_resolver.register_routes()

    def get_server(self) -> FastAPI:
        return self.http_server

    def get_http_server(self) -> FastAPI:
        """Alias for get_server() — kept for backward compatibility."""
        return self.http_server

    def use(self, middleware: type, **options: Any) -> "PyNestApp":
        """Add ASGI middleware to the FastAPI server."""
        self.http_server.add_middleware(middleware, **options)
        return self

    def enable_shutdown_hooks(
        self, signals: Optional[Iterable[signal_module.Signals]] = None
    ) -> "PyNestApp":
        """Register process signal handlers that trigger graceful shutdown."""
        shutdown_signals = tuple(
            signals or (signal_module.SIGTERM, signal_module.SIGINT)
        )
        for shutdown_signal in shutdown_signals:
            signal_module.signal(
                shutdown_signal, self._make_signal_handler(shutdown_signal)
            )
        return self

    async def close(self, signal: Optional[str] = None) -> None:
        """Run graceful application shutdown lifecycle hooks once."""
        if self._closed or self._closing:
            return

        self._closing = True
        try:
            await self.container.shutdown_lifecycle(signal)
            self._closed = True
        finally:
            self._closing = False

    def use_global_filters(self, *filters) -> "PyNestApp":
        """Register one or more exception filters that apply to every route.

        Filters are tried in the order provided. Each filter must be an
        instance of an ExceptionFilter subclass decorated with @Catch.

        Args:
            *filters: ExceptionFilter instances to register globally.

        Returns:
            PyNestApp: The current instance (allows method chaining).

        Example::

            app = PyNestFactory.create(AppModule)
            app.use_global_filters(AllExceptionsFilter())
        """
        for f in filters:
            caught = getattr(f, "__caught_exceptions__", None)
            if caught is None:
                raise ValueError(
                    f"{type(f).__name__} must be decorated with @Catch to use as a global filter"
                )
            exc_types = caught if caught else (Exception,)
            for exc_type in exc_types:
                self._register_global_handler(exc_type, f)
        return self

    def _register_global_handler(self, exc_type: type, filter_instance) -> None:
        async def handler(request: Request, exc: Exception):
            result = filter_instance.catch(exc, None)
            if inspect.isawaitable(result):
                result = await result
            if result is None:
                return JSONResponse(
                    status_code=500, content={"message": "Internal server error"}
                )
            return result

        self.http_server.add_exception_handler(exc_type, handler)

    def _make_signal_handler(self, shutdown_signal: signal_module.Signals):
        def handler(signum, frame):
            self._close_from_signal(self._signal_name(signum or shutdown_signal))

        return handler

    def _close_from_signal(self, signal_name: str) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(self.close(signal_name))
            return

        loop.create_task(self.close(signal_name))

    @staticmethod
    def _signal_name(signum) -> str:
        try:
            return signal_module.Signals(signum).name
        except ValueError:
            return str(signum)

    def _install_lifespan_shutdown(self) -> None:
        original_lifespan_context = self.http_server.router.lifespan_context

        @asynccontextmanager
        async def lifespan_context(app: FastAPI):
            async with original_lifespan_context(app) as state:
                try:
                    yield state
                finally:
                    await self.close()

        self.http_server.router.lifespan_context = lifespan_context
