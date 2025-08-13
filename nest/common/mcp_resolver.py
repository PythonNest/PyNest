from typing import Any


class MCPResolver:
    def __init__(self, container: Any, server: Any):
        # Type of server is FastMCP, but keep Any to avoid hard import at module import time
        self.container = container
        self.server = server

    def register(self):
        for module in self.container.modules.values():
            for controller in module.controllers.values():
                self._register_controller(controller)

    def _register_controller(self, controller: type):
        # Bind methods to the controller class object so that `self` refers to the class
        for attr_name, attr_value in controller.__dict__.items():
            if not callable(attr_value):
                continue

            if hasattr(attr_value, "_mcp_tool"):
                bound_fn = attr_value.__get__(controller, controller)
                meta = getattr(attr_value, "_mcp_tool", {}) or {}
                # Use call-form registration to preserve signature
                self.server.tool(
                    bound_fn,
                    name=meta.get("name"),
                    description=meta.get("description"),
                    tags=meta.get("tags"),
                    output_schema=meta.get("output_schema"),
                    annotations=meta.get("annotations"),
                    exclude_args=meta.get("exclude_args"),
                    meta=meta.get("meta"),
                    enabled=meta.get("enabled"),
                )

            if hasattr(attr_value, "_mcp_resource"):
                bound_fn = attr_value.__get__(controller, controller)
                meta = getattr(attr_value, "_mcp_resource", {}) or {}
                uri = meta.get("uri")
                if not uri:
                    continue
                self.server.add_resource_fn(
                    bound_fn,
                    uri,
                    name=meta.get("name"),
                    description=meta.get("description"),
                    mime_type=meta.get("mime_type"),
                    tags=meta.get("tags"),
                )

            if hasattr(attr_value, "_mcp_prompt"):
                bound_fn = attr_value.__get__(controller, controller)
                meta = getattr(attr_value, "_mcp_prompt", {}) or {}
                self.server.prompt(
                    bound_fn,
                    name=meta.get("name"),
                    description=meta.get("description"),
                    tags=meta.get("tags"),
                    enabled=meta.get("enabled"),
                    meta=meta.get("meta"),
                )