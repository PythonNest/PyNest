from __future__ import annotations

from enum import Enum
from typing import Any, Callable


class HttpMethod(Enum):
    """HTTP methods supported by PyNest routes (engine-neutral)."""
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


# Endpoint is just a callable returning anything — used as a type alias.
Endpoint = Callable[..., Any]


__all__ = ["HttpMethod", "Endpoint"]
