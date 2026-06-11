from __future__ import annotations

import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Any, Optional, Type, TypeVar

from fastapi import FastAPI

from nest.core.pynest_application import PyNestApp
from nest.core.pynest_container import PyNestContainer
from nest.engine.http_adapter import AbstractHttpAdapter

ModuleType = TypeVar("ModuleType")


class AbstractPyNestFactory(ABC):
    @abstractmethod
    def create(self, main_module: Type[ModuleType], **kwargs):
        raise NotImplementedError


class PyNestFactory(AbstractPyNestFactory):
    """Factory that creates a fully-wired PyNest application from a root module."""

    @staticmethod
    def create(
        main_module: Type[ModuleType],
        adapter: Optional[AbstractHttpAdapter] = None,
        **kwargs: Any,
    ) -> PyNestApp:
        """
        Build and return a PyNestApp.

        1. Creates a fresh container (NOT a singleton)
        2. Adds the root module (recursively registers all imported modules)
        3. Validates the dependency graph and builds the injector
        4. Initialises the HTTP engine via the supplied adapter (defaults to FastAPIAdapter)
        5. Registers all routes via RoutesResolver

        Args:
            main_module: The root PyNest module class.
            adapter: Optional HTTP engine adapter. Defaults to FastAPIAdapter.
            **kwargs: Forwarded to the default FastAPIAdapter (and from there to
                FastAPI). When ``adapter=`` is passed explicitly, additional
                kwargs are not allowed — configure the adapter directly instead.
        """
        container = PyNestContainer()
        container.add_module(main_module)
        container.build()
        PyNestFactory._run_async(container.initialize_lifecycle())

        if adapter is None:
            from nest.engines.fastapi import FastAPIAdapter
            adapter = FastAPIAdapter(**kwargs)
        elif kwargs:
            raise TypeError(
                "Cannot pass kwargs to PyNestFactory.create() when adapter= is "
                "set. Pass FastAPI/Litestar/... kwargs to the adapter "
                "constructor instead, e.g. FastAPIAdapter(title='My App')."
            )

        return PyNestApp(container, adapter)

    @staticmethod
    def _create_server(**kwargs) -> FastAPI:
        """Deprecated: kept for backward compatibility with code that called this directly."""
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
