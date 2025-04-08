from typing import Protocol, TypeVar, runtime_checkable

from nest.engine.types import Endpoint


@runtime_checkable
class RouteProtocol(Protocol):
    endpoint: Endpoint
    """Function representing the route endpoint logic."""


Route = TypeVar('Route', bound=RouteProtocol)
