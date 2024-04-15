from typing import Any, Callable, List, Union


def route(method: str, path: Union[str, List[str]] = "/", **kwargs):
    """
    Decorator that defines a route for the controller.

    Args:
        method (str): The HTTP method for the route (GET, POST, DELETE, PUT, PATCH).
        path (Union[str, List[str]]): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.
    """

    def decorator(func):
        func.method = method
        func.__path__ = path
        func.__kwargs__ = kwargs

        return func

    return decorator


# Decorator for defining a GET route with an optional path
Get: Callable[
    [Union[str, List[str]]], Callable[..., Any]
] = lambda path="/", **kwargs: route("GET", path, **kwargs)

# Decorator for defining a POST route with an optional path
Post: Callable[
    [Union[str, List[str]]], Callable[..., Any]
] = lambda path="/", **kwargs: route("POST", path, **kwargs)

# Decorator for defining a DELETE route with an optional path
Delete: Callable[
    [Union[str, List[str]]], Callable[..., Any]
] = lambda path="/", **kwargs: route("DELETE", path, **kwargs)

# Decorator for defining a PUT route with an optional path
Put: Callable[
    [Union[str, List[str]]], Callable[..., Any]
] = lambda path="/", **kwargs: route("PUT", path, **kwargs)

# Decorator for defining a PATCH route with an optional path
Patch: Callable[
    [Union[str, List[str]]], Callable[..., Any]
] = lambda path="/", **kwargs: route("PATCH", path, **kwargs)
