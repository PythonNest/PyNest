from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Union

from fastapi import FastAPI

from nest.engine.http_adapter import AbstractHttpAdapter
from nest.engine.params import ParamSpec
from nest.engine.route_spec import RouteSpec
from nest.engine.types import HttpMethod

if TYPE_CHECKING:
    from nest.core.pynest_container import PyNestContainer


class RoutesResolver:
    """
    Walks the module graph, resolves controller and gateway instances from the
    container, and registers their bound methods via the engine adapter.

    Builds a RouteSpec for each route and calls ``adapter.add_route(spec)``,
    so the engine-specific translation (FastAPI Depends/Body/Query, Litestar
    Parameter, etc.) lives entirely inside the adapter.
    """

    def __init__(
        self,
        container: "PyNestContainer",
        adapter_or_server: Union[AbstractHttpAdapter, FastAPI],
    ) -> None:
        self.container = container
        # Backward-compat: accept either an adapter or a raw FastAPI instance.
        if isinstance(adapter_or_server, AbstractHttpAdapter):
            self.adapter = adapter_or_server
        else:
            from nest.engines.fastapi import FastAPIAdapter
            self.adapter = FastAPIAdapter(instance=adapter_or_server)

    @property
    def app_ref(self):
        """Deprecated — kept for backward compatibility with code that accessed app_ref directly."""
        return self.adapter.get_http_server()

    def register_routes(self) -> None:
        seen_controllers: set = set()
        seen_gateways: set = set()

        for module_ref in self.container.modules.values():
            for controller_class in module_ref.compiled.controllers:
                if controller_class in seen_controllers:
                    continue
                seen_controllers.add(controller_class)
                self._register_controller(controller_class)

            for provider in module_ref.compiled.provider_descriptors:
                gateway_class = provider.use_class
                if gateway_class is None or not hasattr(
                    gateway_class, "__websocket_gateway__"
                ):
                    continue
                if gateway_class in seen_gateways:
                    continue
                seen_gateways.add(gateway_class)
                gateway_instance = self.container.get(provider.provide)
                self._register_gateway(gateway_class, gateway_instance)

    def _register_controller(self, controller_class: type) -> None:
        instance = self.container.get_controller_instance(controller_class)
        tag = getattr(controller_class, "__controller_tag__", None)
        prefix = getattr(controller_class, "__route_prefix__", None) or ""

        for method_name, unbound in inspect.getmembers(
            controller_class, predicate=callable
        ):
            if not hasattr(unbound, "__http_method__"):
                continue
            bound = getattr(instance, method_name)
            self._add_route(bound, unbound, controller_class, prefix, tag)

    def _register_gateway(self, gateway_class: type, gateway_instance: Any) -> None:
        from nest.websockets.gateway import NativeWebSocketGateway

        NativeWebSocketGateway(
            gateway=gateway_instance,
            metadata=getattr(gateway_class, "__websocket_gateway__"),
        ).register(self.adapter.get_http_server())

    def _add_route(
        self,
        bound_method,
        original_method,
        cls: type,
        prefix: str,
        tag: Any,
    ) -> None:
        from nest.core.decorators.controller import _collect_guards
        from nest.core.decorators.http_method import HTTPMethod

        path = getattr(original_method, "__route_path__", "/")
        http_method = getattr(original_method, "__http_method__", None)
        extra_kwargs = dict(getattr(original_method, "__kwargs__", {}))

        if not isinstance(http_method, HTTPMethod):
            return

        full_path = _join_paths(prefix, path)
        status_code = getattr(original_method, "status_code", None)

        guards = tuple(_collect_guards(cls, original_method))
        route_filters = list(getattr(original_method, "__filters__", []))
        controller_filters = list(getattr(cls, "__filters__", []))
        filters = tuple(route_filters + controller_filters)

        # Extract ParamSpecs from the bound method signature.
        params = _extract_param_specs(bound_method)

        spec = RouteSpec(
            method=HttpMethod(http_method.value),
            path=full_path,
            endpoint=bound_method,
            params=params,
            guards=guards,
            filters=filters,
            status_code=status_code,
            tags=(tag,) if tag else (),
            extra=extra_kwargs,
        )
        self.adapter.add_route(spec)


def _extract_param_specs(endpoint) -> tuple:
    """Read ParamSpec defaults off the endpoint's signature into a tuple."""
    try:
        signature = inspect.signature(endpoint)
    except (TypeError, ValueError):
        return ()
    specs = []
    for parameter in signature.parameters.values():
        if isinstance(parameter.default, ParamSpec):
            specs.append(parameter.default)
    return tuple(specs)


def _join_paths(prefix: str, path: str) -> str:
    prefix = prefix or ""
    path = path or "/"
    if not path.startswith("/"):
        path = "/" + path
    combined = prefix.rstrip("/") + path
    if combined.endswith("/") and combined != "/":
        combined = combined.rstrip("/")
    return combined or "/"
