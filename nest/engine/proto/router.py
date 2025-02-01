from typing import Protocol, List, Optional, TypeVar, Iterable, runtime_checkable
from .route import Route
from ..types import Endpoint


@runtime_checkable
class RouterProtocol(Protocol):
    routes: List[Route]
    def __init__(self, tags: Optional[List[str]] = None, **kwargs) -> None: ...
    def include_router(self, router: 'RouterProtocol', **kwargs) -> None: ...
    def add_api_route(self, *, path: str, endpoint: Endpoint, methods: Optional[Iterable[str]]) -> None: ...


Router = TypeVar('Router', bound=RouterProtocol)
