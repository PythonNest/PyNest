from fastapi.routing import APIRouter
from nest.core.decorators.helpers import class_based_view as ClassBasedView


def Controller(tag: str = None, prefix: str = None):
    """
    Decorator that turns a class into a controller, allowing you to define routes using FastAPI decorators.

    Args:
        tag (str, optional): The tag to use for OpenAPI documentation.
        prefix (str, optional): The prefix to use for all routes.

    Returns:
        class: The decorated class.

    """
   # Use tag as default prefix if prefix is None
    if prefix is None:
        prefix = tag

    if not prefix.startswith("/"):
        prefix = "/" + prefix
    if prefix.endswith("/"):
        prefix = prefix[:-1]

    def wrapper(cls) -> ClassBasedView:
        router = APIRouter(tags=[tag] if tag else None)

        http_method_names = ("GET", "POST", "PUT", "DELETE", "PATCH", "ANY")

        for name, method in cls.__dict__.items():
            if callable(method) and hasattr(method, "method"):
                assert (
                    hasattr(method, "__path__") and method.__path__
                ), f"Missing path for method {name}"

                http_method = method.method
                assert http_method in http_method_names, f"Invalid method {http_method}"

                if http_method == "ANY":
                    for supported_method in http_method_names[:-1]:
                        if prefix:
                            method.__path__ = prefix + method.__path__
                        if not method.__path__.startswith("/"):
                            method.__path__ = "/" + method.__path__
                        router.add_api_route(
                            method.__path__, method, methods=[supported_method], **method.__kwargs__
                        )
                else:
                    if prefix:
                        method.__path__ = prefix + method.__path__
                    if not method.__path__.startswith("/"):
                        method.__path__ = "/" + method.__path__
                    router.add_api_route(
                        method.__path__, method, methods=[http_method], **method.__kwargs__
                    )

        def get_router() -> APIRouter:
            return router

        cls.get_router = get_router

        return ClassBasedView(router=router, cls=cls)


def Get(path: str, **kwargs):
    """
    Decorator that defines a GET route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    def decorator(func):
        func.method = "GET"
        func.__path__ = path
        func.__kwargs__ = kwargs
        return func

    return decorator


def Post(path: str, **kwargs):
    """
    Decorator that defines a POST route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    def decorator(func):
        func.method = "POST"
        func.__path__ = path
        func.__kwargs__ = kwargs
        return func

    return decorator


def Delete(path: str, **kwargs):
    """
    Decorator that defines a DELETE route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    def decorator(func):
        func.method = "DELETE"
        func.__path__ = path
        func.__kwargs__ = kwargs
        return func

    return decorator


def Put(path: str, **kwargs):
    """
    Decorator that defines a PUT route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    def decorator(func):
        func.method = "PUT"
        func.__path__ = path
        func.__kwargs__ = kwargs
        return func

    return decorator


def Patch(path: str, **kwargs):
    """
    Decorator that defines a PATCH route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    def decorator(func):
        func.method = "PATCH"
        func.__path__ = path
        func.__kwargs__ = kwargs
        return func

    return decorator


def Any(path: str, **kwargs):
    """
    Decorator that defines a route for the controller with ANY HTTP method.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    def decorator(func):
        func.method = "ANY"
        func.__path__ = path
        func.__kwargs__ = kwargs
        return func

    return decorator

