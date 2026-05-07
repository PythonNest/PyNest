"""
Credit: FastAPI-Utils
Source: https://github.com/dmontagu/fastapi-utils/blob/master/fastapi_utils/cbv.py
"""

import inspect
from typing import (
    Any,
    Callable,
    ClassVar,
    List,
    Type,
    TypeVar,
    Union,
    get_origin,
    get_type_hints,
)

from fastapi import APIRouter, Depends, Request
from starlette.routing import Route, WebSocketRoute

T = TypeVar("T")
K = TypeVar("K", bound=Callable[..., Any])

CBV_CLASS_KEY = "__cbv_class__"


def class_based_view(router: APIRouter, cls: Type[T]) -> Type[T]:
    """
    Replaces any methods of the provided class `cls` that are endpoints of routes in `router` with updated
    function calls that will properly inject an instance of `cls`.
    """
    _init_cbv(cls)
    cbv_router = APIRouter()
    function_members = inspect.getmembers(cls, inspect.isfunction)
    functions_set = set(func for _, func in function_members)
    cbv_routes = [
        route
        for route in router.routes
        if isinstance(route, (Route, WebSocketRoute))
        and route.endpoint in functions_set
    ]
    for route in cbv_routes:
        router.routes.remove(route)
        _update_cbv_route_endpoint_signature(cls, route)
        _wrap_route_with_filters(cls, route)
        cbv_router.routes.append(route)
    router.include_router(cbv_router)
    return cls


def _init_cbv(cls: Type[Any]) -> None:
    """
    Idempotently modifies the provided `cls`, performing the following modifications:
    * The `__init__` function is updated to set any class-annotated dependencies as instance attributes
    * The `__signature__` attribute is updated to indicate to FastAPI what arguments should be passed to the initializer
    """
    if getattr(cls, CBV_CLASS_KEY, False):  # pragma: no cover
        return  # Already initialized
    old_init: Callable[..., Any] = cls.__init__
    old_signature = inspect.signature(old_init)
    old_parameters = list(old_signature.parameters.values())[
        1:
    ]  # drop `self` parameter
    new_parameters = [
        x
        for x in old_parameters
        if x.kind
        not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    ]
    dependency_names: List[str] = []
    for name, hint in get_type_hints(cls).items():
        if get_origin(hint) is ClassVar:
            continue
        parameter_kwargs = {"default": getattr(cls, name, Ellipsis)}
        dependency_names.append(name)
        new_parameters.append(
            inspect.Parameter(
                name=name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation=hint,
                **parameter_kwargs,
            )
        )
    new_signature = old_signature.replace(parameters=new_parameters)

    def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
        for dep_name in dependency_names:
            dep_value = kwargs.pop(dep_name)
            setattr(self, dep_name, dep_value)
        old_init(self, *args, **kwargs)

    setattr(cls, "__signature__", new_signature)
    setattr(cls, "__init__", new_init)
    setattr(cls, CBV_CLASS_KEY, True)


def _update_cbv_route_endpoint_signature(
    cls: Type[Any], route: Union[Route, WebSocketRoute]
) -> None:
    """
    Fixes the endpoint signature for a cbv route to ensure FastAPI performs dependency injection properly.
    """
    old_endpoint = route.endpoint
    old_signature = inspect.signature(old_endpoint)
    old_parameters: List[inspect.Parameter] = list(old_signature.parameters.values())
    old_first_parameter = old_parameters[0]
    new_first_parameter = old_first_parameter.replace(default=Depends(cls))
    new_parameters = [new_first_parameter] + [
        parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY)
        for parameter in old_parameters[1:]
    ]
    new_signature = old_signature.replace(parameters=new_parameters)
    setattr(route.endpoint, "__signature__", new_signature)


def _wrap_route_with_filters(cls: Type[Any], route: Union[Route, WebSocketRoute]) -> None:
    """Wrap a route endpoint with controller/route-level exception filter logic.

    Called after _update_cbv_route_endpoint_signature so the wrapper inherits
    the correct CBV __signature__ (with self as Depends(cls)).
    """
    from nest.common.exceptions import ArgumentsHost

    route_filters = list(getattr(route.endpoint, "__filters__", []))
    controller_filters = list(getattr(cls, "__filters__", []))
    if not route_filters and not controller_filters:
        return

    original_endpoint = route.endpoint
    cbv_signature = getattr(original_endpoint, "__signature__", inspect.signature(original_endpoint))

    # Inject `request: Request` into the wrapper signature so FastAPI provides it.
    existing_params = list(cbv_signature.parameters.values())
    has_request = any(p.name == "request" for p in existing_params)
    if not has_request:
        request_param = inspect.Parameter(
            "request",
            inspect.Parameter.KEYWORD_ONLY,
            annotation=Request,
        )
        wrapper_signature = cbv_signature.replace(parameters=existing_params + [request_param])
    else:
        wrapper_signature = cbv_signature

    orig_param_names = {p.name for p in existing_params}

    async def filter_wrapper(*args, **kwargs):
        request = kwargs.get("request")
        call_kwargs = {k: v for k, v in kwargs.items() if k in orig_param_names}
        try:
            result = original_endpoint(*args, **call_kwargs)
            if inspect.isawaitable(result):
                result = await result
            return result
        except Exception as exc:
            host = ArgumentsHost(request=request)
            for raw_filter in route_filters + controller_filters:
                f = raw_filter() if isinstance(raw_filter, type) else raw_filter
                caught = getattr(f, "__caught_exceptions__", ())
                if not caught or isinstance(exc, caught):
                    result = f.catch(exc, host)
                    if inspect.isawaitable(result):
                        return await result
                    return result
            raise

    filter_wrapper.__name__ = getattr(original_endpoint, "__name__", "filter_wrapper")
    filter_wrapper.__signature__ = wrapper_signature
    route.endpoint = filter_wrapper
