from typing import Any

from nest.common.mcp_resolver import MCPResolver
from nest.core.pynest_app_context import PyNestApplicationContext
from nest.core.pynest_container import PyNestContainer


class PyNestMCPApp(PyNestApplicationContext):
    """
    PyNestMCPApp is the application class for MCP servers in the PyNest framework,
    managing the container and FastMCP server.
    """

    def __init__(self, container: PyNestContainer, mcp_server: Any):
        # Type for mcp_server is FastMCP, kept as Any to avoid hard dependency at import time
        self.container = container
        self.mcp_server = mcp_server
        super().__init__(self.container)
        self.mcp_resolver = MCPResolver(self.container, self.mcp_server)
        self.select_context_module()
        self.register_mcp_items()

    def use(self, middleware: Any) -> "PyNestMCPApp":
        # FastMCP servers expose add_middleware; pass through
        if hasattr(self.mcp_server, "add_middleware"):
            self.mcp_server.add_middleware(middleware)
        return self

    def get_server(self) -> Any:
        return self.mcp_server

    def register_mcp_items(self):
        self.mcp_resolver.register()