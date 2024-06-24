from typing import Type, Optional

from fastapi.routing import APIRouter

from nest.core.decorators.class_based_view import class_based_view as ClassBasedView
from nest.core.decorators.utils import get_instance_variables, parse_dependencies
from nest.core.decorators.http_method import HTTPMethod


def Controller(prefix: Optional[str] = None, tag: Optional[str] = None):
    """
    Decorator that turns a class into a controller, allowing you to define
    routes using FastAPI decorators.

    Args:
        prefix (str, optional): The prefix to use for all routes.
        tag (str, optional): The tag to use for OpenAPI documentation.

    Returns:
        class: The decorated class.
    """

    # Default route_prefix to tag_name if route_prefix is not provided
    route_prefix = process_prefix(prefix, tag)

    def wrapper(cls: Type) -> Type[ClassBasedView]:
        router = APIRouter(tags=[tag] if tag else None)

        # Process class dependencies
        process_dependencies(cls)

        # Set instance variables
        set_instance_variables(cls)

        # Ensure the class has an __init__ method
        ensure_init_method(cls)

        # Add routes to the router
        add_routes(cls, router, route_prefix)

        # Add get_router method to the class
        cls.get_router = classmethod(lambda cls: router)

        return ClassBasedView(router=router, cls=cls)

    return wrapper


def process_prefix(route_prefix: Optional[str], tag_name: Optional[str]) -> str:
    """Process and format the prefix."""
    if route_prefix is None:
        if tag_name is None:
            return None
        else:
            route_prefix = tag_name

    if not route_prefix.startswith("/"):
        route_prefix = "/" + route_prefix

    if route_prefix.endswith("/"):
        route_prefix = route_prefix.rstrip("/")

    return route_prefix


def process_dependencies(cls: Type) -> None:
    """Parse and set dependencies for the class."""
    dependencies = parse_dependencies(cls)
    setattr(cls, "__dependencies__", dependencies)


def set_instance_variables(cls: Type) -> None:
    """Set instance variables for the class."""
    non_dependency_vars = get_instance_variables(cls)
    for key, value in non_dependency_vars.items():
        setattr(cls, key, value)


def ensure_init_method(cls: Type) -> None:
    """Ensure the class has an __init__ method."""
    if not hasattr(cls, "__init__"):
        raise AttributeError("Class must have an __init__ method")
    try:
        delattr(cls, "__init__")
    except AttributeError:
        pass


def add_routes(cls: Type, router: APIRouter, route_prefix: str) -> None:
    """Add routes from class methods to the router."""
    for method_name, method_function in cls.__dict__.items():
        if callable(method_function) and hasattr(method_function, "__http_method__"):
            validate_method_decorator(method_function, method_name)
            configure_method_route(method_function, route_prefix)
            add_route_to_router(router, method_function)


def validate_method_decorator(method_function: callable, method_name: str) -> None:
    """Validate that the method has a proper HTTP method decorator."""
    if (
        not hasattr(method_function, "__route_path__")
        or not method_function.__route_path__
    ):
        raise AssertionError(f"Missing path for method {method_name}")

    if not isinstance(method_function.__http_method__, HTTPMethod):
        raise AssertionError(f"Invalid method {method_function.__http_method__}")


def configure_method_route(method_function: callable, route_prefix: str) -> None:
    """Configure the route for the method."""
    if not method_function.__route_path__.startswith("/"):
        method_function.__route_path__ = "/" + method_function.__route_path__

    method_function.__route_path__ = (
        route_prefix + method_function.__route_path__
        if route_prefix
        else method_function.__route_path__
    )

    # remove trailing "/" fro __route_path__
    # it converts "/api/users/" to "/api/users"
    if (
        method_function.__route_path__ != "/"
        and method_function.__route_path__.endswith("/")
    ):
        method_function.__route_path__ = method_function.__route_path__.rstrip("/")


def add_route_to_router(router: APIRouter, method_function: callable) -> None:
    """Add the configured route to the router."""
    route_kwargs = {
        "path": method_function.__route_path__,
        "endpoint": method_function,
        "methods": [method_function.__http_method__.value],
        **method_function.__kwargs__,
    }

    if hasattr(method_function, "status_code"):
        route_kwargs["status_code"] = method_function.status_code

    router.add_api_route(**route_kwargs)
