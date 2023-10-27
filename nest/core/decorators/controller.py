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
    if prefix:
        if not prefix.startswith("/"):
            prefix = "/" + prefix
        if prefix.endswith("/"):
            prefix = prefix[:-1]

    def wrapper(cls) -> ClassBasedView:
        router = APIRouter(tags=[tag] if tag else None)

        for name, method in cls.__dict__.items():
            if callable(method) and hasattr(method, "method"):
                if not method.__path__:
                    raise Exception("Missing path")
                else:
                    if prefix:
                        method.__path__ = prefix + method.__path__
                    if not method.__path__.startswith("/"):
                        method.__path__ = "/" + method.__path__
                    if method.method == "GET":
                        router.add_api_route(
                            method.__path__,
                            method,
                            methods=["GET"],
                            **method.__kwargs__
                        )
                    elif method.method == "POST":
                        router.add_api_route(
                            method.__path__,
                            method,
                            methods=["POST"],
                            **method.__kwargs__
                        )
                    elif method.method == "PUT":
                        router.add_api_route(
                            method.__path__,
                            method,
                            methods=["PUT"],
                            **method.__kwargs__
                        )
                    elif method.method == "DELETE":
                        router.add_api_route(
                            method.__path__,
                            method,
                            methods=["DELETE"],
                            **method.__kwargs__
                        )
                    elif method.method == "PATCH":
                        router.add_api_route(
                            method.__path__,
                            method,
                            methods=["PATCH"],
                            **method.__kwargs__
                        )
                    else:
                        raise Exception("Invalid method")

        def get_router() -> APIRouter:
            """
            Returns:
                APIRouter: The router associated with the controller.
            """
            return router

        cls.get_router = get_router

        return ClassBasedView(router=router, cls=cls)
    return wrapper