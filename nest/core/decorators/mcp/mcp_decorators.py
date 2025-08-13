from typing import Optional

from nest.core.decorators.utils import get_instance_variables, parse_dependencies


def McpController():
    def decorator(cls):
        dependencies = parse_dependencies(cls)
        setattr(cls, "__dependencies__", dependencies)

        non_dep = get_instance_variables(cls)
        for key, value in non_dep.items():
            setattr(cls, key, value)

        # Align behavior with other controllers: if __init__ exists, remove it;
        # do not raise if already removed by another decorator
        try:
            delattr(cls, "__init__")
        except AttributeError:
            pass

        return cls

    return decorator


def McpTool(name: Optional[str] = None, **kwargs):
    def decorator(func):
        metadata = {"name": name}
        metadata.update(kwargs)
        setattr(func, "_mcp_tool", metadata)
        return func

    return decorator


def McpResource(uri: str, **kwargs):
    def decorator(func):
        if not uri or not isinstance(uri, str):
            raise ValueError("McpResource requires a non-empty URI string")
        metadata = {"uri": uri}
        metadata.update(kwargs)
        setattr(func, "_mcp_resource", metadata)
        return func

    return decorator


def McpPrompt(name: Optional[str] = None, **kwargs):
    def decorator(func):
        metadata = {"name": name}
        metadata.update(kwargs)
        setattr(func, "_mcp_prompt", metadata)
        return func

    return decorator