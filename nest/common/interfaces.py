from __future__ import annotations

from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class OnModuleInit(Protocol):
    def on_module_init(self) -> Any: ...


@runtime_checkable
class OnApplicationBootstrap(Protocol):
    def on_application_bootstrap(self) -> Any: ...


@runtime_checkable
class BeforeApplicationShutdown(Protocol):
    def before_application_shutdown(self, signal: Optional[str]) -> Any: ...


@runtime_checkable
class OnModuleDestroy(Protocol):
    def on_module_destroy(self) -> Any: ...


@runtime_checkable
class OnApplicationShutdown(Protocol):
    def on_application_shutdown(self, signal: Optional[str]) -> Any: ...
