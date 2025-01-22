# nest/core/pynest_factory.py

from typing import Type, TypeVar, Optional
from nest.core.pynest_application import PyNestApp
from nest.core.pynest_container import PyNestContainer
from nest.core.protocols import WebFrameworkAdapterProtocol
from nest.core.adapters.fastapi.fastapi_adapter import FastAPIAdapter

ModuleType = TypeVar("ModuleType")


class PyNestFactory:
    """Factory class for creating PyNest applications."""

    @staticmethod
    def create(
        main_module: Type[ModuleType],
        adapter: Optional[WebFrameworkAdapterProtocol] = None,
        **kwargs
    ) -> PyNestApp:
        """
        Create a PyNest application with the specified main module class
        and a chosen adapter (defaults to FastAPIAdapter if none given).
        """
        if adapter is None:
            adapter = FastAPIAdapter()  # Default to FastAPI

        container = PyNestContainer()
        container.add_module(main_module)

        # Create the PyNest application
        app = PyNestApp(container=container, adapter=adapter)

        # Optionally add middlewares here before running
        # app.use_middleware(SomeMiddlewareClass, optionA=123)

        return app
