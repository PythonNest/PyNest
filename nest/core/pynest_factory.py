from typing import TypeVar

from fastapi import FastAPI

from nest.core.pynest_application import PyNestApp
from nest.core.pynest_container import PyNestContainer

T = TypeVar("T")


class PyNestFactory:
    @staticmethod
    def _initialize(
        module: T,
        container: PyNestContainer,
    ):
        container.add_module(module)

    @staticmethod
    def create(main_module: T, **kwargs) -> PyNestApp:
        container = PyNestContainer()
        http_server = PyNestFactory._create_server(**kwargs)
        PyNestFactory._initialize(main_module, container)
        app = PyNestApp(container, http_server)
        return app

    @staticmethod
    def _create_server(**kwargs) -> FastAPI:
        return FastAPI(**kwargs)
