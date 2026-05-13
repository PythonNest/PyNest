from __future__ import annotations

import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Type, TypeVar

from fastapi import FastAPI

from nest.core.pynest_application import PyNestApp
from nest.core.pynest_container import PyNestContainer

ModuleType = TypeVar("ModuleType")


class AbstractPyNestFactory(ABC):
    @abstractmethod
    def create(self, main_module: Type[ModuleType], **kwargs):
        raise NotImplementedError


class PyNestFactory(AbstractPyNestFactory):
    """Factory that creates a fully-wired PyNest application from a root module."""

    @staticmethod
    def create(main_module: Type[ModuleType], **kwargs) -> PyNestApp:
        """
        Build and return a PyNestApp.

        1. Creates a fresh container (NOT a singleton)
        2. Adds the root module (recursively registers all imported modules)
        3. Validates the dependency graph and builds the injector
        4. Creates the FastAPI HTTP server
        5. Registers all routes via RoutesResolver
        """
        container = PyNestContainer()
        container.add_module(main_module)
        container.build()
        PyNestFactory._run_async(container.initialize_lifecycle())

        http_server = FastAPI(**kwargs)
        return PyNestApp(container, http_server)

    @staticmethod
    def _create_server(**kwargs) -> FastAPI:
        return FastAPI(**kwargs)

    @staticmethod
    def _run_async(coro):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)

        result = {}

        def runner():
            try:
                result["value"] = asyncio.run(coro)
            except BaseException as exc:
                result["error"] = exc

        thread = threading.Thread(target=runner)
        thread.start()
        thread.join()
        if "error" in result:
            raise result["error"]
        return result.get("value")
