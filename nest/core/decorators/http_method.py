from typing import Callable, List, Union, TypeVar, TypeAlias
from enum import Enum
import sys

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec


P = ParamSpec("P")
R = TypeVar("R")
Func: TypeAlias = Callable[[P], R]

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


def route(http_method: HTTPMethod, route_path: Union[str, List[str]] = "/", **kwargs) -> Callable[[Func], Func]:
    """
    Decorator that defines a route for the controller.

    Args:
        http_method (HTTPMethod): The HTTP method for the route (GET, POST, DELETE, PUT, PATCH).
        route_path (Union[str, List[str]]): The route path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function, preserving the signature.
    """

    def decorator(func: Func) -> Func:

        # Add custom route metadata
        func.__http_method__ = http_method
        func.__route_path__ = route_path
        func.__kwargs__ = kwargs

        return func

    return decorator


def Get(route_path: Union[str, List[str]] = "/", **kwargs):
    return route(HTTPMethod.GET, route_path, **kwargs)


def Post(route_path: Union[str, List[str]] = "/", **kwargs):
    return route(HTTPMethod.POST, route_path, **kwargs)


def Delete(route_path: Union[str, List[str]] = "/", **kwargs):
    return route(HTTPMethod.DELETE, route_path, **kwargs)


def Put(route_path: Union[str, List[str]] = "/", **kwargs):
    return route(HTTPMethod.PUT, route_path, **kwargs)


def Patch(route_path: Union[str, List[str]] = "/", **kwargs):
    return route(HTTPMethod.PATCH, route_path, **kwargs)


def Head(route_path: Union[str, List[str]] = "/", **kwargs):
    return route(HTTPMethod.HEAD, route_path, **kwargs)


def Options(route_path: Union[str, List[str]] = "/", **kwargs):
    return route(HTTPMethod.OPTIONS, route_path, **kwargs)
