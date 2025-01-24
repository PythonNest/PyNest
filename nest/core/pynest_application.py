# nest/core/pynest_application.py

from typing import Any
from nest.core.protocols import WebFrameworkAdapterProtocol
from nest.core.pynest_app_context import (
    PyNestApplicationContext,
)


class PyNestApp(PyNestApplicationContext):
    def __init__(self, container, adapter: WebFrameworkAdapterProtocol):
        super().__init__(container)
        self.adapter = adapter
        self._is_listening = False

        # Register all routes
        self.adapter.register_routes(self.container)

        # Create and configure the web application via the adapter
        self.web_app = self.adapter.create_app()

    def use_middleware(self, middleware_cls: type, **options: Any) -> "PyNestApp":
        """
        Add middleware to the application.
        """
        self.adapter.add_middleware(middleware_cls, **options)
        return self

    @property
    def is_listening(self) -> bool:
        return self._is_listening
