from typing import Any

from nest.core.decorators.helpers import route_decorator


def Get(path: str, **kwargs: Any):
    """
    Decorator that defines a GET route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    return route_decorator(path, "GET", **kwargs)


def Post(path: str, **kwargs: Any):
    """
    Decorator that defines a POST route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    return route_decorator(path, "POST", **kwargs)


def Delete(path: str, **kwargs: Any):
    """
    Decorator that defines a DELETE route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    return route_decorator(path, "DELETE", **kwargs)


def Put(path: str, **kwargs: Any):
    """
    Decorator that defines a PUT route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    return route_decorator(path, "PUT", **kwargs)


def Patch(path: str, **kwargs: Any):
    """
    Decorator that defines a PATCH route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    return route_decorator(path, "PATCH", **kwargs)
