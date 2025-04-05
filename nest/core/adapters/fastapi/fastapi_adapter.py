from typing import Any, Callable, List, Optional
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware import Middleware

from nest.core.protocols import (
    WebFrameworkAdapterProtocol,
    RouterProtocol,
    Container,
)

from nest.core.adapters.fastapi.utils import wrap_instance_method


class FastAPIRouterAdapter(RouterProtocol):
    """
    An adapter for registering routes in FastAPI.
    """

    def __init__(self, base_path: str = "") -> None:
        """
        Initialize with an optional base path.
        """
        print("Initializing FastAPIRouterAdapter")
        self._base_path = base_path
        self._router = APIRouter(prefix=self._base_path)

    def add_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: List[str],
        *,
        name: Optional[str] = None,
    ) -> None:
        """
        Register an HTTP route with FastAPI's APIRouter.
        """
        self._router.add_api_route(path, endpoint, methods=methods, name=name)

    def get_router(self) -> APIRouter:
        """
        Return the underlying FastAPI APIRouter.
        """
        return self._router


###############################################################################
# FastAPI Adapter
###############################################################################


class FastAPIAdapter(WebFrameworkAdapterProtocol):
    """
    A FastAPI-based implementation of WebFrameworkAdapterProtocol.
    """

    def __init__(self) -> None:
        self._app: Optional[FastAPI] = None
        self._router_adapter = FastAPIRouterAdapter()
        self._middlewares: List[Middleware] = []
        self._initialized = False

    def create_app(self, **kwargs: Any) -> FastAPI:
        """
        Create and configure the FastAPI application.
        """
        print("Creating FastAPI app")
        self._app = FastAPI(**kwargs)
        self._app.include_router(self._router_adapter.get_router())
        # Add any pre-collected middlewares
        for mw in self._middlewares:
            self._app.add_middleware(mw.cls, **mw.options)

        self._initialized = True
        return self._app

    def get_router(self) -> RouterProtocol:
        """
        Return the RouterProtocol implementation.
        """
        return self._router_adapter

    def add_middleware(
        self,
        middleware_cls: Any,
        **options: Any,
    ) -> None:
        """
        Add middleware to the FastAPI application.
        """
        if not self._app:
            # Collect middlewares before app creation
            self._middlewares.append(Middleware(middleware_cls, **options))
        else:
            # Add middleware directly if app is already created
            self._app.add_middleware(middleware_cls, **options)

    def run(self, host: str = "127.0.0.1", port: int = 8000, **kwargs) -> None:
        """
        Run the FastAPI application using Uvicorn.
        """
        if not self._initialized or not self._app:
            raise RuntimeError("FastAPI app not created yet. Call create_app() first.")

        uvicorn.run(self._app, host=host, port=port, **kwargs)

    async def startup(self) -> None:
        """
        Handle any startup tasks if necessary.
        """
        if self._app:
            await self._app.router.startup()

    async def shutdown(self) -> None:
        """
        Handle any shutdown tasks if necessary.
        """
        if self._app:
            await self._app.router.shutdown()

    def register_routes(self, container: Container) -> None:
        """
        Register multiple routes at once.
        """
        for module in container.modules.values():
            for controller_cls in module.controllers.values():
                instance = container.get_instance(controller_cls)

                route_definitions = getattr(controller_cls, "__pynest_routes__", [])
                for route_definition in route_definitions:
                    path = route_definition["path"]
                    method = route_definition["method"]
                    original_method = route_definition["endpoint"]

                    final_endpoint = wrap_instance_method(
                        instance, controller_cls, original_method
                    )

                    self._router_adapter.add_route(
                        path=path,
                        endpoint=final_endpoint,
                        methods=[method],
                        name=f"{controller_cls.__name__}.{original_method.__name__}",
                    )
