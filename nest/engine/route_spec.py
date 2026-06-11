from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple

from nest.engine.params import ParamSpec
from nest.engine.types import HttpMethod


@dataclass(frozen=True)
class RouteSpec:
    method: HttpMethod
    path: str
    endpoint: Callable[..., Any]
    params: Tuple[ParamSpec, ...] = ()
    guards: Tuple[Any, ...] = ()
    filters: Tuple[Any, ...] = ()
    status_code: Optional[int] = None
    tags: Tuple[str, ...] = ()
    name: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


__all__ = ["RouteSpec"]
