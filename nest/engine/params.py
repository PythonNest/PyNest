from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple

VALID_SOURCES = (
    "body",
    "query",
    "path",
    "header",
    "request",
    "response",
    "ip",
    "host",
    "custom",
)


@dataclass(frozen=True)
class ParamSpec:
    source: str
    name: Optional[str] = None
    annotation: Any = None
    default: Any = ...
    pipes: Tuple[Any, ...] = ()
    factory: Optional[Callable[[Any, Any], Any]] = None
    data: Any = None

    def __post_init__(self) -> None:
        if self.source not in VALID_SOURCES:
            raise ValueError(
                f"Invalid param source {self.source!r}. "
                f"Must be one of: {VALID_SOURCES}"
            )


__all__ = ["ParamSpec", "VALID_SOURCES"]
