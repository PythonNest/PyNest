from typing import Protocol, TypeVar, List, Optional, Iterable

from nest.engine.proto.router import Router
from nest.engine.proto.route import Route
from nest.engine.types import Endpoint

Middleware = TypeVar('Middleware')


class AppProtocol(Protocol):

    def __init__(self, **kwargs) -> None: ...
    def add_middleware(self, middleware: Middleware, **options) -> None: ...
    def include_router(self, router: Router, *, prefix: str = "", tags: Optional[List[str]] = None, **options) -> None: ...
    def add_api_route(self, *, path: str, endpoint: Endpoint, methods: Optional[Iterable[str]]) -> None: ...
    @property
    def routes(self) -> List[Route]: ...


App = TypeVar('App', bound=AppProtocol)
