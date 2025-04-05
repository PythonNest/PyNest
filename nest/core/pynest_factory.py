from typing import Type, TypeVar, Optional
from nest.core.pynest_application import PyNestApp
from nest.core.pynest_container import PyNestContainer
from nest.core.protocols import WebFrameworkAdapterProtocol

ModuleType = TypeVar("ModuleType")


def adapter_map(adapter: str) -> WebFrameworkAdapterProtocol:
    if adapter == "fastapi":
        from nest.core.adapters.fastapi.fastapi_adapter import FastAPIAdapter

        return FastAPIAdapter()
    else:
        raise ValueError(f"Unknown adapter: {adapter}")


class PyNestFactory:
    """Factory class for creating PyNest applications."""

    @staticmethod
    def create(
        main_module: Type[ModuleType], adapter: Optional[str] = "fastapi", **kwargs
    ) -> PyNestApp:
        """
        Create a PyNest application with the specified main module class
        and a chosen adapter (defaults to FastAPIAdapter if none given).
        """
        # Get the adapter instance
        if adapter is None:
            adapter = "fastapi"

        adapter = adapter_map(adapter)
        container = PyNestContainer()
        container.add_module(main_module)

        # Create the PyNest application
        app = PyNestApp(container=container, adapter=adapter)

        # Optionally add middlewares here before running
        # app.use_middleware(SomeMiddlewareClass, optionA=123)

        return app
