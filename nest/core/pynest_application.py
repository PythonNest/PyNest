from __future__ import annotations

from typing import Any

from fastapi import FastAPI

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
