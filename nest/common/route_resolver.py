from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, FastAPI, Request
from nest.common.decorators import has_param_decorators, wrap_param_decorators

if TYPE_CHECKING:
    from nest.core.pynest_container import PyNestContainer


class RoutesResolver:
    """
    Walks the module graph, resolves controller and gateway instances from the
    container, and registers their bound methods on the FastAPI app.
    """

    def __init__(self, container: "PyNestContainer", app_ref: FastAPI) -> None:
        self.container = container
        self.app_ref = app_ref

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

        router = APIRouter(tags=[tag] if tag else None)

        for method_name, unbound in inspect.getmembers(
            controller_class, predicate=callable
        ):
            if not hasattr(unbound, "__http_method__"):
                continue
            bound = getattr(instance, method_name)
            self._add_route(router, bound, unbound, controller_class, prefix)

        self.app_ref.include_router(router)

    def _register_gateway(self, gateway_class: type, gateway_instance: Any) -> None:
        from nest.websockets.gateway import NativeWebSocketGateway

        NativeWebSocketGateway(
            gateway=gateway_instance,
            metadata=getattr(gateway_class, "__websocket_gateway__"),
        ).register(self.app_ref)

    def _add_route(
        self,
        router: APIRouter,
        bound_method,
        original_method,
        cls: type,
        prefix: str,
    ) -> None:
        from nest.core.decorators.controller import _collect_guards
        from nest.core.decorators.http_method import HTTPMethod

        path = getattr(original_method, "__route_path__", "/")
        http_method = getattr(original_method, "__http_method__", None)
        extra_kwargs = getattr(original_method, "__kwargs__", {})

        if not isinstance(http_method, HTTPMethod):
            return

        full_path = _join_paths(prefix, path)

        route_kwargs = {
            "path": full_path,
            "endpoint": bound_method,
            "methods": [http_method.value],
            **extra_kwargs,
        }

        if has_param_decorators(bound_method):
            route_kwargs["endpoint"] = wrap_param_decorators(bound_method)

        if hasattr(original_method, "status_code"):
            route_kwargs["status_code"] = original_method.status_code

        guards = _collect_guards(cls, original_method)
        if guards:
            route_kwargs["dependencies"] = [g.as_dependency() for g in guards]

        route_filters = list(getattr(original_method, "__filters__", []))
        controller_filters = list(getattr(cls, "__filters__", []))
        if route_filters or controller_filters:
            route_kwargs["endpoint"] = _wrap_with_filters(
                route_kwargs["endpoint"], route_filters + controller_filters
            )

        router.add_api_route(**route_kwargs)


def _wrap_with_filters(endpoint, filters) -> callable:
    """Wrap a bound-method endpoint with exception filter logic."""
    from nest.common.exceptions import ArgumentsHost

    original_sig = inspect.signature(endpoint)
    existing_params = list(original_sig.parameters.values())
    has_request = any(p.name == "request" for p in existing_params)

    if not has_request:
        request_param = inspect.Parameter(
            "request",
            inspect.Parameter.KEYWORD_ONLY,
            annotation=Request,
        )
        wrapper_sig = original_sig.replace(parameters=existing_params + [request_param])
    else:
        wrapper_sig = original_sig

    orig_param_names = {p.name for p in existing_params}

    async def filter_wrapper(*args, **kwargs):
        request = kwargs.get("request")
        call_kwargs = {k: v for k, v in kwargs.items() if k in orig_param_names}
        try:
            result = endpoint(*args, **call_kwargs)
            if inspect.isawaitable(result):
                result = await result
            return result
        except Exception as exc:
            host = ArgumentsHost(request=request)
            for raw_filter in filters:
                f = raw_filter() if isinstance(raw_filter, type) else raw_filter
                caught = getattr(f, "__caught_exceptions__", ())
                if not caught or isinstance(exc, caught):
                    result = f.catch(exc, host)
                    if inspect.isawaitable(result):
                        return await result
                    return result
            raise

    filter_wrapper.__name__ = getattr(endpoint, "__name__", "filter_wrapper")
    filter_wrapper.__signature__ = wrapper_sig
    return filter_wrapper


def _join_paths(prefix: str, path: str) -> str:
    prefix = prefix or ""
    path = path or "/"
    if not path.startswith("/"):
        path = "/" + path
    combined = prefix.rstrip("/") + path
    if combined.endswith("/") and combined != "/":
        combined = combined.rstrip("/")
    return combined or "/"
