"""
Translation layer: ParamSpec → FastAPI param markers.

For each ParamSpec attached to an endpoint's parameter defaults, build a
FastAPI-compatible dependency (Depends-wrapped) that resolves the value from
the request and applies pipes, then wrap the endpoint with a new signature
that FastAPI understands.

This is the heaviest piece of the FastAPI adapter — it mirrors what NestJS's
adapter would do for Express/Fastify but at a higher level because FastAPI
itself owns body parsing, validation, and OpenAPI generation.
"""
from __future__ import annotations

import inspect
import keyword
import typing
from typing import Any, Callable, Optional, Tuple

from fastapi import Body as FABody
from fastapi import Depends
from fastapi import Header as FAHeader
from fastapi import HTTPException
from fastapi import Path as FAPath
from fastapi import Query as FAQuery
from fastapi import Request, Response
from pydantic import TypeAdapter

from nest.engine.execution_context import ExecutionContext
from nest.engine.params import ParamSpec


def has_param_specs(endpoint: Callable) -> bool:
    """True if any parameter of ``endpoint`` has a ParamSpec default."""
    signature = inspect.signature(endpoint)
    return any(
        isinstance(parameter.default, ParamSpec)
        for parameter in signature.parameters.values()
    )


def bind_params(endpoint: Callable) -> Callable:
    """
    Return a wrapper function that FastAPI can route to.

    The wrapper signature has FastAPI-flavored defaults (Body/Query/Path/Header
    + Depends) so FastAPI's dependency injection populates them, then the wrapper
    forwards resolved values to the original endpoint.
    """
    signature = inspect.signature(endpoint)

    # Resolve string annotations from `from __future__ import annotations`.
    try:
        resolved_hints = typing.get_type_hints(endpoint)
    except Exception:
        resolved_hints = {}

    wrapped_parameters = []
    for parameter in signature.parameters.values():
        resolved_annotation = resolved_hints.get(parameter.name, parameter.annotation)
        if resolved_annotation is not parameter.annotation:
            parameter = parameter.replace(annotation=resolved_annotation)

        if isinstance(parameter.default, ParamSpec):
            dependency = _build_dependency(parameter)
            wrapped_parameters.append(
                parameter.replace(
                    annotation=inspect.Parameter.empty,
                    default=Depends(dependency),
                )
            )
        else:
            wrapped_parameters.append(parameter)

    resolved_return = resolved_hints.get("return", signature.return_annotation)
    wrapper_signature = signature.replace(
        parameters=wrapped_parameters,
        return_annotation=resolved_return,
    )
    handler_param_names = set(signature.parameters)

    async def wrapper(*args, **kwargs):
        call_kwargs = {k: v for k, v in kwargs.items() if k in handler_param_names}
        result = endpoint(*args, **call_kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    wrapper.__name__ = getattr(endpoint, "__name__", "param_decorator_wrapper")
    wrapper.__signature__ = wrapper_signature
    wrapper.__annotations__ = {k: v for k, v in resolved_hints.items()}
    return wrapper


# ─── internals ────────────────────────────────────────────────────────────────


def _build_dependency(parameter: inspect.Parameter) -> Callable:
    spec: ParamSpec = parameter.default
    annotation = parameter.annotation

    async def dependency(**kwargs):
        value = await _resolve_value(spec, kwargs)
        value = await _apply_pipes(value, spec.pipes)
        return _coerce_value(value, annotation)

    dependency.__name__ = f"resolve_{parameter.name}_{spec.source}"
    dependency.__signature__ = _dependency_signature(parameter, spec)
    return dependency


async def _resolve_value(spec: ParamSpec, kwargs: dict) -> Any:
    request = kwargs.get("request")
    response = kwargs.get("response")

    if spec.source == "request":
        return request
    if spec.source == "response":
        return response
    if spec.source == "path" and spec.name is None:
        return dict(request.path_params)
    if spec.source == "query" and spec.name is None:
        return dict(request.query_params)
    if spec.source == "header" and spec.name is None:
        return dict(request.headers)
    if spec.source == "ip":
        return request.client.host if request.client else None
    if spec.source == "host":
        if spec.name:
            return request.path_params.get(spec.name)
        return request.url.hostname
    if spec.source == "custom":
        context = ExecutionContext(request, response)
        result = spec.factory(spec.data, context)
        if inspect.isawaitable(result):
            return await result
        return result

    return _first_source_value(kwargs)


def _dependency_signature(
    parameter: inspect.Parameter, spec: ParamSpec,
) -> inspect.Signature:
    source = spec.source
    annotation = parameter.annotation

    if source == "request":
        return inspect.Signature(parameters=[inspect.Parameter(
            "request", inspect.Parameter.KEYWORD_ONLY, annotation=Request)])

    if source == "response":
        return inspect.Signature(parameters=[inspect.Parameter(
            "response", inspect.Parameter.KEYWORD_ONLY, annotation=Response)])

    if source in {"path", "query", "header"} and spec.name is None:
        return _request_only_signature()
    if source in {"ip", "host"}:
        return _request_only_signature()

    if source == "custom":
        return inspect.Signature(parameters=[
            inspect.Parameter("request", inspect.Parameter.KEYWORD_ONLY, annotation=Request),
            inspect.Parameter("response", inspect.Parameter.KEYWORD_ONLY, annotation=Response),
        ])

    if source == "body":
        name = _source_parameter_name(spec.name or parameter.name)
        default = _default_value(spec)
        fa_default = FABody(default, alias=spec.name, embed=spec.name is not None)
        return inspect.Signature(parameters=[inspect.Parameter(
            name, inspect.Parameter.KEYWORD_ONLY, annotation=annotation, default=fa_default,
        )])

    if source == "path":
        name = _source_parameter_name(spec.name or parameter.name)
        alias = None if name == (spec.name or parameter.name) else spec.name
        fa_default = FAPath(..., alias=alias)
        return inspect.Signature(parameters=[inspect.Parameter(
            name, inspect.Parameter.KEYWORD_ONLY, annotation=annotation, default=fa_default,
        )])

    if source == "query":
        return _simple_source_signature(parameter, spec,
            lambda d, alias: FAQuery(d, alias=alias))

    if source == "header":
        return _simple_source_signature(parameter, spec,
            lambda d, alias: FAHeader(d, alias=alias))

    return inspect.Signature()


def _simple_source_signature(parameter, spec, marker_factory) -> inspect.Signature:
    source_name = spec.name or parameter.name
    name = _source_parameter_name(source_name)
    alias = source_name if name != source_name or spec.name else None
    fa_default = marker_factory(_default_value(spec), alias)
    return inspect.Signature(parameters=[inspect.Parameter(
        name, inspect.Parameter.KEYWORD_ONLY, annotation=parameter.annotation, default=fa_default,
    )])


def _request_only_signature() -> inspect.Signature:
    return inspect.Signature(parameters=[inspect.Parameter(
        "request", inspect.Parameter.KEYWORD_ONLY, annotation=Request)])


def _source_parameter_name(name: str) -> str:
    if name and name.isidentifier() and not keyword.iskeyword(name):
        return name
    return "value"


def _default_value(spec: ParamSpec) -> Any:
    if spec.default is ...:
        return ...
    return spec.default


def _first_source_value(kwargs: dict) -> Any:
    for key, value in kwargs.items():
        if key not in {"request", "response"}:
            return value
    return None


async def _apply_pipes(value: Any, pipes: Tuple[Any, ...]) -> Any:
    for pipe in pipes:
        pipe_instance = pipe() if inspect.isclass(pipe) else pipe
        try:
            if hasattr(pipe_instance, "transform"):
                value = pipe_instance.transform(value)
            elif callable(pipe_instance):
                value = pipe_instance(value)
            else:
                raise TypeError("Pipe must be callable or expose a transform method")
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if inspect.isawaitable(value):
            value = await value
    return value


def _coerce_value(value: Any, annotation: Any) -> Any:
    if value is None or annotation in {inspect.Parameter.empty, Any}:
        return value
    if inspect.isclass(annotation) and isinstance(value, annotation):
        return value
    return TypeAdapter(annotation).validate_python(value)
