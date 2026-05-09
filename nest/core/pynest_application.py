from __future__ import annotations

import inspect
from typing import Any

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
