"""
PyNest parameter decorators — engine-neutral.

These factory functions produce ``ParamSpec`` instances that the engine adapter
(default ``FastAPIAdapter``) translates into its framework's native param
markers. Under the FastAPI adapter, the translation lives in
``nest/engines/fastapi/params.py``.

Backward-compat aliases:
- ``ParamMetadata`` is an alias for ``ParamSpec``
- ``ExecutionContext`` re-exports from ``nest.engine.execution_context``
- ``has_param_decorators`` and ``wrap_param_decorators`` re-export the FastAPI
  binding helpers so legacy callers continue to work.
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Tuple

# Public re-exports (backward compatibility)
from nest.engine.execution_context import (
    ExecutionContext,
    HttpExecutionContext,
)
from nest.engine.params import ParamSpec

# ParamMetadata used to be the FastAPI-aware dataclass; it now aliases ParamSpec.
ParamMetadata = ParamSpec


def Body(key: Optional[str] = None, *pipes: Any, default: Any = ...) -> ParamSpec:
    key, pipes = _normalize_name_and_pipes(key, pipes)
    return ParamSpec(source="body", name=key, pipes=pipes, default=default)


def Param(name: Optional[str] = None, *pipes: Any, default: Any = ...) -> ParamSpec:
    name, pipes = _normalize_name_and_pipes(name, pipes)
    return ParamSpec(source="path", name=name, pipes=pipes, default=default)


def Query(name: Optional[str] = None, *pipes: Any, default: Any = ...) -> ParamSpec:
    name, pipes = _normalize_name_and_pipes(name, pipes)
    return ParamSpec(source="query", name=name, pipes=pipes, default=default)


def Headers(name: Optional[str] = None, *pipes: Any, default: Any = ...) -> ParamSpec:
    name, pipes = _normalize_name_and_pipes(name, pipes)
    return ParamSpec(source="header", name=name, pipes=pipes, default=default)


def Req() -> ParamSpec:
    return ParamSpec(source="request")


def Res() -> ParamSpec:
    return ParamSpec(source="response")


def Ip(*pipes: Any, default: Any = ...) -> ParamSpec:
    return ParamSpec(source="ip", pipes=pipes, default=default)


def HostParam(name: Optional[str] = None, *pipes: Any, default: Any = ...) -> ParamSpec:
    name, pipes = _normalize_name_and_pipes(name, pipes)
    return ParamSpec(source="host", name=name, pipes=pipes, default=default)


def createParamDecorator(
    factory: Callable[[Any, ExecutionContext], Any],
) -> Callable:
    """Build a reusable param decorator backed by a user-supplied factory."""
    if not callable(factory):
        raise TypeError("createParamDecorator requires a callable factory")

    def decorator(data: Any = None, *pipes: Any, default: Any = ...) -> ParamSpec:
        return ParamSpec(
            source="custom",
            data=data,
            factory=factory,
            pipes=pipes,
            default=default,
        )

    return decorator


# ── backward-compat re-exports ────────────────────────────────────────────────
# These used to live here and contained FastAPI-specific logic. Now they're
# thin re-exports from the FastAPI adapter so legacy callers continue to work.


def has_param_decorators(endpoint: Callable) -> bool:
    """Deprecated alias — use ``has_param_specs`` from ``nest.engines.fastapi.params``."""
    from nest.engines.fastapi.params import has_param_specs
    return has_param_specs(endpoint)


def wrap_param_decorators(endpoint: Callable) -> Callable:
    """Deprecated alias — use ``bind_params`` from ``nest.engines.fastapi.params``."""
    from nest.engines.fastapi.params import bind_params
    return bind_params(endpoint)


# ── internals ────────────────────────────────────────────────────────────────


def _normalize_name_and_pipes(name: Any, pipes: Tuple[Any, ...]):
    if name is not None and not isinstance(name, str):
        return None, (name, *pipes)
    return name, pipes


__all__ = [
    "Body",
    "Param",
    "Query",
    "Headers",
    "Req",
    "Res",
    "Ip",
    "HostParam",
    "ExecutionContext",
    "HttpExecutionContext",
    "ParamMetadata",
    "ParamSpec",
    "createParamDecorator",
    "has_param_decorators",
    "wrap_param_decorators",
]
