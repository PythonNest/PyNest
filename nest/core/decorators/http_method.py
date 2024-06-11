from enum import Enum
from typing import Any, Callable, List, Union


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


def route(http_method: HTTPMethod, route_path: Union[str, List[str]] = "/", **kwargs):
    """
    Decorator that defines a route for the controller.

    Args:
        http_method (HTTPMethod): The HTTP method for the route (GET, POST, DELETE, PUT, PATCH).
        route_path (Union[str, List[str]]): The route path for the route. example: "/users"
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.
    """

    def decorator(func):
        func.__http_method__ = http_method
        func.__route_path__ = route_path
        func.__kwargs__ = kwargs

        return func

    return decorator


# Decorator for defining a GET route with an optional path
Get: Callable[[Union[str, List[str]]], Callable[..., Any]] = (
    lambda route_path="/", **kwargs: route(HTTPMethod.GET, route_path, **kwargs)
)

# Decorator for defining a POST route with an optional path
Post: Callable[[Union[str, List[str]]], Callable[..., Any]] = (
    lambda route_path="/", **kwargs: route(HTTPMethod.POST, route_path, **kwargs)
)

# Decorator for defining a DELETE route with an optional path
Delete: Callable[[Union[str, List[str]]], Callable[..., Any]] = (
    lambda route_path="/", **kwargs: route(HTTPMethod.DELETE, route_path, **kwargs)
)

# Decorator for defining a PUT route with an optional path
Put: Callable[[Union[str, List[str]]], Callable[..., Any]] = (
    lambda route_path="/", **kwargs: route(HTTPMethod.PUT, route_path, **kwargs)
)

# Decorator for defining a PATCH route with an optional path
Patch: Callable[[Union[str, List[str]]], Callable[..., Any]] = (
    lambda route_path="/", **kwargs: route(HTTPMethod.PATCH, route_path, **kwargs)
)
