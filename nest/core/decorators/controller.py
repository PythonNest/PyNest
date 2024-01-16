from fastapi.routing import APIRouter
from nest.core.decorators.helpers import class_based_view as ClassBasedView
from nest.common.constants import STATUS_CODE_TOKEN


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

    # Ensure prefix has correct formatting
    if prefix:
        prefix = "/" + prefix.rstrip("/")

    def wrapper(cls) -> ClassBasedView:
        router = APIRouter(tags=[tag] if tag else None)

        http_method_names = ("GET", "POST", "PUT", "DELETE", "PATCH")

        for name, method in cls.__dict__.items():
            if callable(method) and hasattr(method, "method"):
                # Check if method is decorated with an HTTP method decorator
                assert (
                    hasattr(method, "__path__") and method.__path__
                ), f"Missing path for method {name}"

                http_method = method.method
                # Ensure that the method is a valid HTTP method
                assert http_method in http_method_names, f"Invalid method {http_method}"

                # Process single path or list of paths
                paths = (
                    method.__path__
                    if isinstance(method.__path__, list)
                    else [method.__path__]
                )

                for path in paths:
                    if prefix and isinstance(path, str):
                        path = (
                            f"{prefix.rstrip('/')}/{path.lstrip('/')}"
                            if path
                            else prefix.rstrip("/")
                        )

                        # Set default status code if  provided in @HttpCode decorator
                    if (
                        hasattr(method, STATUS_CODE_TOKEN)
                        and method.__kwargs__.get(STATUS_CODE_TOKEN) is None
                    ):
                        method.__kwargs__[STATUS_CODE_TOKEN] = method.__dict__[
                            STATUS_CODE_TOKEN
                        ]
                    router.add_api_route(
                        path, method, methods=[http_method], **method.__kwargs__
                    )

        def get_router() -> APIRouter:
            """
            Returns:
                APIRouter: The router associated with the controller.
            """
            return router

        cls.get_router = get_router

        return ClassBasedView(router=router, cls=cls)

    return wrapper
