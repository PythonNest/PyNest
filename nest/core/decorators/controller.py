from typing import Optional, Type

from nest.core.decorators.http_method import HTTPMethod
from nest.core.decorators.utils import get_instance_variables, parse_dependencies


def Controller(prefix: Optional[str] = None, tag: Optional[str] = None):
    """
    Decorator that marks a class as a controller, collecting route metadata
    for future registration in the underlying framework.

    Args:
        prefix (str, optional): The prefix to use for all routes.
        tag (str, optional): The tag to use for grouping or doc generation.

    Returns:
        class: The decorated class (with route metadata added).
    """

    route_prefix = process_prefix(prefix, tag)

    def wrapper(cls: Type) -> Type:
        # 1. Process class-level dependencies
        process_dependencies(cls)

        # 2. Set instance variables for any non-injected fields
        set_instance_variables(cls)

        # 3. Ensure the class has an __init__ method
        ensure_init_method(cls)

        # 4. Gather route metadata
        route_definitions = collect_route_definitions(cls, route_prefix)

        # 5. Store routes in class attribute for later usage
        setattr(cls, "__pynest_routes__", route_definitions)

        # (Optional) Store prefix / tag for doc generation
        setattr(cls, "__pynest_prefix__", route_prefix)
        setattr(cls, "__pynest_tag__", tag)

        return cls

    return wrapper


def process_prefix(route_prefix: Optional[str], tag_name: Optional[str]) -> str:
    """Process and format the prefix."""
    if route_prefix is None:
        if tag_name is None:
            return ""
        else:
            route_prefix = tag_name

    if not route_prefix.startswith("/"):
        route_prefix = "/" + route_prefix

    # Remove any trailing slash to keep consistent
    route_prefix = route_prefix.rstrip("/")
    return route_prefix


def process_dependencies(cls: Type) -> None:
    """Parse and set dependencies for the class (via your DI system)."""
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
        raise AttributeError(f"{cls.__name__} must have an __init__ method")

    # We do the same removal trick if needed
    try:
        delattr(cls, "__init__")
    except AttributeError:
        pass


def collect_route_definitions(cls: Type, base_prefix: str):
    """Scan class methods for HTTP method decorators and build route metadata."""
    route_definitions = []
    for method_name, method_function in cls.__dict__.items():
        if callable(method_function) and hasattr(method_function, "__http_method__"):
            validate_method_decorator(method_function, method_name)
            configure_method_route(method_function, base_prefix)

            route_info = {
                "path": method_function.__route_path__,
                "method": method_function.__http_method__.value,
                "endpoint": method_function,
                "kwargs": method_function.__kwargs__,
                "status_code": getattr(method_function, "status_code", None),
                "name": f"{cls.__name__}.{method_name}",
            }
            route_definitions.append(route_info)
    return route_definitions


def validate_method_decorator(method_function: callable, method_name: str) -> None:
    """Validate that the method has a proper HTTP method decorator."""
    if not hasattr(method_function, "__route_path__") or not method_function.__route_path__:
        raise AssertionError(f"Missing path for method {method_name}")

    if not isinstance(method_function.__http_method__, HTTPMethod):
        raise AssertionError(f"Invalid method {method_function.__http_method__}")


def configure_method_route(method_function: callable, base_prefix: str) -> None:
    """Configure the final route path by prepending base_prefix."""
    raw_path = method_function.__route_path__

    if not raw_path.startswith("/"):
        raw_path = "/" + raw_path

    # Combine prefix + path
    full_path = f"{base_prefix}{raw_path}"
    full_path = full_path.rstrip("/") if full_path != "/" else full_path

    method_function.__route_path__ = full_path
