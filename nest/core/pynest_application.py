from fastapi import FastAPI
from pynest_app_context import PyNestApplicationContext
from typing import Any, Dict, List, Union
from pynest_container import PyNestContainer
from nest.common.route_resolver import RoutesResolver


class PyNestApp(PyNestApplicationContext):
    _is_listening = False

    @property
    def is_listening(self):
        self._is_listening

    def __init__(self, container: PyNestContainer, http_server: FastAPI):
        self.container = container
        self.http_server = http_server
        super().__init__(self.container)
        self.routes_resolver = RoutesResolver(self.container, self.http_server)
        self.select_context_module()

        self.register_routes()

    def use(self, middleware: type, **options: Any) -> None:
        self.http_server.add_middleware(middleware, **options)
        return self

    def get_server(self):
        return self.http_server

    def enable_cors(self, options: Dict[str, Union[str, bool, List[str]]]):
        """
        Configure Cross-Origin Resource Sharing (CORS) for the HTTP server.

        :param options: A dictionary containing the CORS configuration options.
        :type options: Dict[str, Union[str, bool, List[str]]]

        :raises ValueError: If an unexpected key is passed in the `options` dictionary.
        :Expected keys: allow_origins, allow_credentials, allow_headers, allow_methods

        Example usage:
        >>> cors_options = {
        ...     "allow_origins": ["example.com", "test.com"],
        ...     "allow_credentials": True,
        ...     "allow_methods": ["GET", "POST"],
        ...     "allow_headers": ["Content-Type", "Authorization"]
        ... }
        """
        from fastapi.middleware.cors import CORSMiddleware

        # Define the expected keys
        expected_keys = [
            "allow_origins",
            "allow_credentials",
            "allow_methods",
            "allow_headers",
        ]

        # Check for unexpected keys
        unexpected_keys = [key for key in options if key not in expected_keys]
        if unexpected_keys:
            raise ValueError(f"Unexpected keys in options: {unexpected_keys}")

        # Extract options
        allow_origins = options.get("allow_origins", [])
        allow_credentials = options.get("allow_credentials", True)
        allow_methods = options.get("allow_methods", ["*"])
        allow_headers = options.get("allow_headers", ["*"])

        # Configure CORS using CORSMiddleware
        cors_middleware = CORSMiddleware(
            allow_origins=allow_origins,
            allow_credentials=allow_credentials,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
        )

        # Add the CORS middleware to the HTTP server
        self.http_server.add_middleware(cors_middleware)

    def register_routes(self):
        self.routes_resolver.register_routes()
