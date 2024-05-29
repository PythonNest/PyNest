from typing import Any

from fastapi import FastAPI

from nest.common.route_resolver import RoutesResolver
from nest.core.pynest_app_context import PyNestApplicationContext
from nest.core.pynest_container import PyNestContainer


class PyNestApp(PyNestApplicationContext):
    """
    PyNestApp is the main application class for the PyNest framework,
    managing the container and HTTP server.
    """

    _is_listening = False

    @property
    def is_listening(self) -> bool:
        return self._is_listening

    def __init__(self, container: PyNestContainer, http_server: FastAPI):
        """
        Initialize the PyNestApp with the given container and HTTP server.

        Args:
            container (PyNestContainer): The PyNestContainer container instance.
            http_server (FastAPI): The FastAPI server instance.
        """
        self.container = container
        self.http_server = http_server
        super().__init__(self.container)
        self.routes_resolver = RoutesResolver(self.container, self.http_server)
        self.select_context_module()
        self.register_routes()

    def use(self, middleware: type, **options: Any) -> "PyNestApp":
        """
        Add middleware to the FastAPI server.

        Args:
            middleware (type): The middleware class.
            **options (Any): Additional options for the middleware.

        Returns:
            PyNestApp: The current instance of PyNestApp, allowing method chaining.
        """
        self.http_server.add_middleware(middleware, **options)
        return self

    def get_server(self) -> FastAPI:
        """
        Get the FastAPI server instance.

        Returns:
            FastAPI: The FastAPI server instance.
        """
        return self.http_server

    def register_routes(self):
        """
        Register the routes using the RoutesResolver.
        """
        self.routes_resolver.register_routes()
