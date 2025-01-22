# protocols.py

from __future__ import annotations
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
    Generic,
)

###############################################################################
# 1. REQUEST & RESPONSE
###############################################################################

@runtime_checkable
class RequestProtocol(Protocol):
    """
    Abstract representation of an HTTP request.
    """

    @property
    def method(self) -> str:
        """
        HTTP method (GET, POST, PUT, DELETE, etc.).
        """
        ...

    @property
    def url(self) -> str:
        """
        The full request URL (or path).
        """
        ...

    @property
    def headers(self) -> Dict[str, str]:
        """
        A dictionary of header names to values.
        """
        ...

    @property
    def cookies(self) -> Dict[str, str]:
        """
        A dictionary of cookie names to values.
        """
        ...

    @property
    def query_params(self) -> Dict[str, str]:
        """
        A dictionary of query parameter names to values.
        """
        ...

    @property
    def path_params(self) -> Dict[str, Any]:
        """
        A dictionary of path parameter names to values.
        Usually extracted from the URL pattern.
        """
        ...

    async def body(self) -> Union[bytes, str]:
        """
        Return the raw request body (bytes or text).
        """
        ...


@runtime_checkable
class ResponseProtocol(Protocol):
    """
    Abstract representation of an HTTP response.
    """

    def set_status_code(self, status_code: int) -> None:
        """
        Set the HTTP status code (e.g. 200, 404, etc.).
        """
        ...

    def set_header(self, name: str, value: str) -> None:
        """
        Set a single header on the response.
        """
        ...

    def set_cookie(self, name: str, value: str, **options: Any) -> None:
        """
        Set a cookie on the response.
        'options' might include expires, domain, secure, httponly, etc.
        """
        ...

    def delete_cookie(self, name: str, **options: Any) -> None:
        """
        Instruct the browser to delete a cookie (by setting an expired cookie).
        """
        ...

    def set_body(self, content: Union[str, bytes]) -> None:
        """
        Set the final body (string or bytes).
        (You might add overloads for JSON or streaming in a real system.)
        """
        ...

    def set_json(self, data: Any, status_code: Optional[int] = None) -> None:
        """
        Encode data as JSON, set the body, and optionally set the status code.
        """
        ...


###############################################################################
# 2. ROUTING & HTTP METHODS
###############################################################################

@runtime_checkable
class RouteDefinition(Protocol):
    """
    Represents a single route definition: path, HTTP methods, etc.
    """
    path: str
    http_methods: List[str]
    endpoint: Callable[..., Any]
    name: Optional[str]


@runtime_checkable
class RouterProtocol(Protocol):
    """
    A protocol for registering routes, websocket endpoints,
    or other specialized routes (SSE, GraphQL, etc.).
    """

    def add_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: List[str],
        *,
        name: Optional[str] = None,
    ) -> None:
        """
        Register a normal HTTP endpoint at the given path with the given methods.
        Example: GET/POST/PUT, etc.
        """
        ...

    def add_websocket_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        name: Optional[str] = None,
    ) -> None:
        """
        Register a WebSocket endpoint at the given path.
        """
        ...


Container = TypeVar("Container")

@runtime_checkable
class WebFrameworkAdapterProtocol(Protocol):
    """
    High-level interface for an HTTP framework adapter.
    The PyNest system can call these methods to:
      - create and manage the main application object
      - get a RouterProtocol to register routes
      - add middlewares
      - run the server
      - optionally handle startup/shutdown hooks, etc.
    """

    def create_app(self, **kwargs: Any) -> Any:
        """
        Create and store the main web application object.
        **kwargs** can pass parameters (e.g., title, debug, etc.).
        Returns the native app object (like FastAPI instance).
        """
        ...

    def get_router(self) -> RouterProtocol:
        """
        Return a RouterProtocol for the main router (or a sub-router).
        """
        ...

    def add_middleware(
        self,
        middleware_cls: Any,
        **options: Any,
    ) -> None:
        """
        Add a middleware class to the application, with config options.
        """
        ...

    def run(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """
        Blockingly run the HTTP server on the given host/port.
        In production, you might prefer to return an ASGI app
        and let an external server (e.g., gunicorn) run it.
        """
        ...

    async def startup(self) -> None:
        """
        Optional: If the framework has an 'on_startup' event, run it.
        """
        ...

    async def shutdown(self) -> None:
        """
        Optional: If the framework has an 'on_shutdown' event, run it.
        """
        ...

    def register_routes(self, container: Container) -> None:
        """
        Register multiple routes at once.
        """
        ...


@runtime_checkable
class CLIAdapterProtocol(Protocol):
    """
    High-level interface for an CLI adapter.
    The PyNest system can call these methods to:
      - create and manage the main application object
      - run the cli app
      - register commands into the cli
    """

    def create_app(self, **kwargs: Any) -> Any:
        """
        Create and store the main CLI application object.
        **kwargs** can pass parameters
        Returns the native app object (like FastAPI instance).
        """
        ...

    def get_router(self) -> RouterProtocol:
        """
        Return a RouterProtocol for the main router (or a sub-router).
        """
        ...

    def add_middleware(
        self,
        middleware_cls: Any,
        **options: Any,
    ) -> None:
        """
        Add a middleware class to the application, with config options.
        """
        ...

    def run(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """
        Blockingly run the HTTP server on the given host/port.
        In production, you might prefer to return an ASGI app
        and let an external server (e.g., gunicorn) run it.
        """
        ...

    async def startup(self) -> None:
        """
        Optional: If the framework has an 'on_startup' event, run it.
        """
        ...

    async def shutdown(self) -> None:
        """
        Optional: If the framework has an 'on_shutdown' event, run it.
        """
        ...

    def register_routes(self, container: Container) -> None:
        """
        Register multiple routes at once.
        """
        ...




###############################################################################
# 3. PARAMETER EXTRACTION (NEST-JS LIKE)
###############################################################################

T = TypeVar("T")


class RequestAttribute:
    """
    Marker/base class for typed request attributes
    like Param, Query, Header, Cookie, etc.
    """
    ...


class Param(Generic[T], RequestAttribute):
    """
    Usage:
      def get_item(self, id: Param[int]): ...
    """
    pass


class Query(Generic[T], RequestAttribute):
    """
    Usage:
      def search(self, q: Query[str]): ...
    """
    pass


class Header(Generic[T], RequestAttribute):
    """
    Usage:
      def do_something(self, token: Header[str]): ...
    """
    pass


class Cookie(Generic[T], RequestAttribute):
    """
    Usage:
      def show_info(self, user_id: Cookie[str]): ...
    """
    pass


class Body(Generic[T], RequestAttribute):
    """
    Usage:
      def create_user(self, data: Body[UserDTO]): ...
    """
    pass


class Form(Generic[T], RequestAttribute):
    """
    Usage:
      def post_form(self, form_data: Form[LoginForm]): ...
    """
    pass


class File(Generic[T], RequestAttribute):
    """
    Usage:
      def upload(self, file: File[UploadedFile]): ...
    """
    pass


class RawRequest(RequestAttribute):
    """
    Sometimes you just need the entire request object.
    Usage:
      def debug(self, req: RawRequest): ...
    """
    pass

###############################################################################
# 4. ERROR HANDLING
###############################################################################

@runtime_checkable
class HTTPExceptionProtocol(Protocol):
    """
    A standardized interface for raising an HTTP exception or error
    that can be recognized by the underlying framework.
    """
    status_code: int
    detail: str

    def to_response(self) -> ResponseProtocol:
        """
        Convert this exception into a protocol-level response
        (or a native framework response).
        """
        ...


@runtime_checkable
class ExceptionHandlerProtocol(Protocol):
    """
    For registering custom exception handlers.
    """

    def handle_exception(self, exc: Exception) -> ResponseProtocol:
        """
        Given an exception, return a response.
        """
        ...


###############################################################################
# 5. MIDDLEWARE & FILTERS
###############################################################################

@runtime_checkable
class MiddlewareProtocol(Protocol):
    """
    A protocol for middleware classes/functions
    that can be added to the application.
    """

    def __call__(self, request: RequestProtocol, call_next: Callable) -> Any:
        """
        Some frameworks pass 'call_next' to chain the next handler.
        Others might do this differently.
        This is just an abstract representation.
        """
        ...


@runtime_checkable
class FilterProtocol(Protocol):
    """
    A smaller, more focused pre/post processing "filter"
    that can manipulate requests or responses.
    Could be integrated as an alternative or layer on top of middleware.
    """

    def before_request(self, request: RequestProtocol) -> None:
        ...

    def after_request(self, request: RequestProtocol, response: ResponseProtocol) -> None:
        ...


###############################################################################
# 6. SECURITY & AUTH
###############################################################################

@runtime_checkable
class AuthGuardProtocol(Protocol):
    """
    Something that checks authentication or authorization
    and possibly raises an HTTP exception if unauthorized.
    """

    def check(self, request: RequestProtocol) -> None:
        """
        If the user is not authorized, raise an error (HTTPExceptionProtocol).
        Otherwise, do nothing.
        """
        ...
