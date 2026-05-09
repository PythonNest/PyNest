from __future__ import annotations

from typing import List, Optional, Type

from injector import inject as injector_inject


def Controller(prefix: Optional[str] = None, tag: Optional[str] = None):
    """
    Marks a class as a PyNest controller.

    Stores route prefix and tag as class metadata only. Does NOT wrap the class,
    delete __init__, or set class-level dependency attributes.
    The injector resolves controller instances; RoutesResolver registers bound methods.

    Args:
        prefix: URL prefix for all routes in this controller (e.g. "/users")
        tag:    OpenAPI tag for Swagger docs
    """

    def wrapper(cls: Type) -> Type:
        route_prefix = _process_prefix(prefix, tag)

        cls.__is_controller__ = True
        cls.__route_prefix__ = route_prefix
        cls.__controller_tag__ = tag

        # Mark constructor for injector auto-wiring (same guard as @Injectable)
        own_init = cls.__dict__.get("__init__")
        if own_init is not None and getattr(own_init, "__annotations__", None):
            injector_inject(cls)

        return cls

    return wrapper


def _process_prefix(route_prefix: Optional[str], tag_name: Optional[str]) -> Optional[str]:
    if route_prefix is None and tag_name is None:
        return None
    if route_prefix is None:
        route_prefix = tag_name
    if not route_prefix.startswith("/"):
        route_prefix = "/" + route_prefix
    if route_prefix.endswith("/") and route_prefix != "/":
        route_prefix = route_prefix.rstrip("/")
    return route_prefix


def _collect_guards(cls: Type, method) -> List:
    guards = list(getattr(cls, "__guards__", []))
    guards.extend(getattr(method, "__guards__", []))
    return guards
