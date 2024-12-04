from abc import ABC, abstractmethod
from typing import Type, TypeVar

from fastapi import FastAPI

from nest.core.pynest_container import PyNestContainer
from nest.core.pynest_factory import AbstractPyNestFactory, ModuleType
from nest.web.pynest_fastapi_application import PyNestFastapiApp


class PyNestWebFactory(AbstractPyNestFactory):
    """Factory class for creating PyNest applications."""

    @staticmethod
    def create(main_module: Type[ModuleType], **kwargs) -> PyNestFastapiApp:
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
        http_server = PyNestWebFactory._create_server(**kwargs)
        return PyNestFastapiApp(container, http_server)

    @staticmethod
    def _create_server(**kwargs) -> FastAPI:
        """
        Create a FastAPI server.

        Args:
            **kwargs: Additional keyword arguments for the FastAPI server.

        Returns:
            FastAPI: The created FastAPI server.
        """
        return FastAPI(**kwargs)
