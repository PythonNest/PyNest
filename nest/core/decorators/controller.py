from fastapi.routing import APIRouter

from nest.core.decorators.class_based_view import class_based_view as ClassBasedView
from nest.core.decorators.utils import get_instance_variables, parse_dependencies
from nest.core.decorators.http_method import HTTPMethod


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

        dependencies = parse_dependencies(cls)
        setattr(cls, "__dependencies__", dependencies)
        non_dep = get_instance_variables(cls)
        for key, value in non_dep.items():
            setattr(cls, key, value)
        try:
            delattr(cls, "__init__")
        except AttributeError:
            raise AttributeError("Class must have an __init__ method")

        for name, method in cls.__dict__.items():
            if callable(method) and hasattr(method, "method"):
                # Check if method is decorated with an HTTP method decorator
                assert (
                    hasattr(method, "__path__") and method.__path__
                ), f"Missing path for method {name}"

                http_method = method.method
                # Ensure that the method is a valid HTTP method
                assert isinstance(
                    http_method, HTTPMethod
                ), f"Invalid method {http_method}"

                if prefix:
                    method.__path__ = prefix + method.__path__
                if not method.__path__.startswith("/"):
                    method.__path__ = "/" + method.__path__

                route_kwargs = {
                    "path": method.__path__,
                    "endpoint": method,
                    "methods": [http_method.value],
                    **method.__kwargs__,
                }

                if hasattr(method, "status_code"):
                    route_kwargs["status_code"] = method.status_code

                router.add_api_route(**route_kwargs)

        def get_router() -> APIRouter:
            """
            Returns:
                APIRouter: The router associated with the controller.
            """
            return router

        cls.get_router = get_router

        return ClassBasedView(router=router, cls=cls)

    return wrapper
