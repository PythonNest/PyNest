from typing import Any
from contextlib import asynccontextmanager

from fastapi import FastAPI

from nest.common.route_resolver import RoutesResolver
from nest.core.pynest_app_context import PyNestApplicationContext
from nest.core.pynest_container import PyNestContainer
from nest.core.apscheduler import start_scheduler, stop_scheduler
from nest.core.decorators.scheduler import activate_scheduled_methods_for_instance


class PyNestApp(PyNestApplicationContext):
    """
    PyNestApp is the main application class for the PyNest framework,
    managing the container and HTTP server.
    """

    _is_listening = False

    @property
    def is_listening(self) -> bool:
        return self._is_listening

    def __init__(self, container: PyNestContainer, http_server: FastAPI):
        """
        Initialize the PyNestApp with the given container and HTTP server.

        Args:
            container (PyNestContainer): The PyNestContainer container instance.
            http_server (FastAPI): The FastAPI server instance.
        """
        self.container = container
        self.http_server = http_server
        super().__init__(self.container)
        self.routes_resolver = RoutesResolver(self.container, self.http_server)
        self.select_context_module()
        self.register_routes()
        
        # Activate scheduled methods for all instantiated services
        self._activate_scheduled_methods()
        
        # Setup lifecycle events for scheduler
        self._setup_scheduler_lifecycle()

    def _setup_scheduler_lifecycle(self):
        """
        Sets up lifecycle events to start and stop the scheduler.
        """
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            start_scheduler()
            yield
            # Shutdown
            stop_scheduler()
        
        self.http_server.router.lifespan_context = lifespan

    def _activate_scheduled_methods(self):
        """
        Activate scheduled methods for all instantiated services in the container.
        """
        try:
            # Get all modules from the container
            for module in self.container.modules.values():
                # Get all providers from each module
                for provider_name, provider_class in module.providers.items():
                    try:
                        # Get the instance from the container
                        instance = self.container.get_instance(provider_class)
                        if instance is not None:
                            activate_scheduled_methods_for_instance(instance)
                    except Exception as e:
                        # Log the error for this specific provider but continue
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.debug(f"Could not activate scheduled methods for {provider_name}: {e}")
        except Exception as e:
            # Log the error but don't fail the application startup
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error activating scheduled methods: {e}")

    def use(self, middleware: type, **options: Any) -> "PyNestApp":
        """
        Add middleware to the FastAPI server.

        Args:
            middleware (type): The middleware class.
            **options (Any): Additional options for the middleware.

        Returns:
            PyNestApp: The current instance of PyNestApp, allowing method chaining.
        """
        self.http_server.add_middleware(middleware, **options)
        return self

    def get_server(self) -> FastAPI:
        """
        Get the FastAPI server instance.

        Returns:
            FastAPI: The FastAPI server instance.
        """
        return self.http_server

    def register_routes(self):
        """
        Register the routes using the RoutesResolver.
        """
        self.routes_resolver.register_routes()