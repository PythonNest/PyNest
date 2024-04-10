from typing import Any

from fastapi import FastAPI

from nest.common.route_resolver import RoutesResolver
from nest.core.pynest_app_context import PyNestApplicationContext
from nest.core.pynest_container import PyNestContainer


class PyNestApp(PyNestApplicationContext):
    _is_listening = False

    @property
    def is_listening(self):
        return self._is_listening

    def __init__(self, container: PyNestContainer, http_server: FastAPI):
        self.container = container
        self.http_server = http_server
        super().__init__(self.container)
        self.routes_resolver = RoutesResolver(self.container, self.http_server)
        self.select_context_module()
        self.register_routes()

    def use(self, middleware: type, **options: Any) -> None:
        self.http_server.add_middleware(middleware, **options)
        return self

    def get_server(self):
        return self.http_server

    def register_routes(self):
        self.routes_resolver.register_routes()
