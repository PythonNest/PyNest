from typing import Type, TypeVar, Any

from nest.core.pynest_container import PyNestContainer
from nest.core.pynest_mcp_application import PyNestMCPApp
from nest.core.pynest_factory import AbstractPyNestFactory

ModuleType = TypeVar("ModuleType")


class MCPFactory(AbstractPyNestFactory):
    """Factory class for creating PyNest MCP applications."""

    @staticmethod
    def create(main_module: Type[ModuleType], **kwargs) -> PyNestMCPApp:
        """
        Create a PyNest MCP application with the specified main module class.

        Args:
            main_module (ModuleType): The main module for the PyNest application.
            **kwargs: Additional keyword arguments forwarded to FastMCP constructor
                      (e.g., name, instructions, version).

        Returns:
            PyNestMCPApp: The created PyNest MCP application.
        """
        container = PyNestContainer()
        container.add_module(main_module)

        # Lazy import to avoid hard dependency when MCP is not used
        try:
            from fastmcp import FastMCP  # type: ignore
        except Exception as e:  # pragma: no cover - environment without fastmcp
            raise ImportError(
                "fastmcp is required to use MCPFactory. Install with `pip install fastmcp`"
            ) from e

        # Ensure a default name for the MCP server
        if "name" not in kwargs:
            kwargs["name"] = "PyNest MCP Server"
        mcp_server = FastMCP(**kwargs)
        return PyNestMCPApp(container, mcp_server)