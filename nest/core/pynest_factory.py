from typing import Type, TypeVar, overload, Union, Optional

from nest.core.pynest_application import PyNestApp
from nest.core.pynest_container import PyNestContainer
from nest.engine.proto import App
from nest.engine.fastapi import FastAPIApp


ModuleType = TypeVar("ModuleType")


class PyNestFactory:
    """Factory class for creating PyNest applications."""

    @staticmethod
    @overload
    def create(
        main_module: Type[ModuleType],
        app_cls: Type[FastAPIApp],
        title: str = "",
        description: str = "",
        version: Optional[Union[str, int, float]] = None,
        debug: bool = False,
    ) -> PyNestApp:
        """
            Create a PyNest application of FastAPIApp kind.
        """

    @staticmethod
    @overload
    def create(
        main_module: Type[ModuleType],
        app_cls: Type[App],
    ) -> PyNestApp:
        """
            Create a PyNest application of FastAPIApp kind.
        """

    @staticmethod
    def create(
        main_module: Type[ModuleType],
        app_cls: Type[App] = FastAPIApp,
        **kwargs
    ) -> PyNestApp:
        """
        Create a PyNest application with the specified main module class.

        Args:
            main_module (ModuleType): The main module for the PyNest application.
            **kwargs: Additional keyword arguments for the FastAPI server.

        Returns:
            PyNestApp: The created PyNest application.
        """
        container = PyNestContainer()
        container.add_module(main_module)
        http_server = PyNestFactory._create_server(app_cls, **kwargs)
        return PyNestApp(container, http_server)

    @staticmethod
    def _create_server(app_cls: Type[App], **kwargs) -> App:
        """
        Create a FastAPI server.

        Args:
            **kwargs: Additional keyword arguments for the FastAPI server.

        Returns:
            FastAPI: The created FastAPI server.
        """
        return app_cls(**kwargs)
