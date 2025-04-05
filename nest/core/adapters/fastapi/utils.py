from typing import Callable, Annotated, get_origin, get_args, Optional, Any, Union

from fastapi import (
    Path,
    Query,
    Header,
    Body,
    File,
    UploadFile,
    Response,
    Request,
    BackgroundTasks,
    Form,
    Cookie,
    Depends,
)
from nest.core.protocols import (
    Param,
    Query as QueryParam,
    Header as HeaderParam,
    Body as BodyParam,
    Cookie as CookieParam,
    File as FileParam,
    Form as FormParam,
    BackgroundTasks as BackgroundTasksParam,
)
import functools
import inspect
import typing


def _provide_bg_tasks(bg: BackgroundTasks) -> BackgroundTasks:
    """
    A simple dependency function: FastAPI will inject
    its `BackgroundTasks` object as 'bg' here, and we return it.
    """
    return bg


def wrap_instance_method(
    instance,
    cls,
    method: Callable,
) -> Callable:
    """
    1. Create a new plain function that calls `method(instance, ...)`.
    2. Rewrite its signature so that 'self' is removed, and Param/Query/Body become Annotated[...] for FastAPI.
    3. Return that new function, which you can pass to fastapi's router.

    This avoids "invalid method signature" by not rewriting the bound method in place.
    """

    # The unbound function object:
    if hasattr(method, "__func__"):
        # If 'method' is a bound method, get the actual function
        unbound_func = method.__func__
    else:
        # If it's already an unbound function, use it
        unbound_func = method

    # Create a wrapper function that calls the unbound function with 'instance' as the first arg
    @functools.wraps(unbound_func)
    def wrapper(*args, **kwargs):
        return unbound_func(instance, *args, **kwargs)

    # Now rewrite the wrapper's signature:
    # - removing 'self'
    # - converting Param/Query/Body to Annotated
    new_wrapper = rewrite_signature_for_fastapi(wrapper)
    return new_wrapper


def rewrite_signature_for_fastapi(func: Callable) -> Callable:
    """
    Modify the function's signature:
      - Remove 'self' if it's the first param
      - Convert Param[T], QueryParam[T], HeaderParam[T], BodyParam[T],
        CookieParam[T], FormParam[T], FileParam[T] into Annotated[InnerType, fastapi.Param(...)]
      - Handle nested types like Optional and Union
      - Leave special FastAPI types (Request, Response, BackgroundTasks, UploadFile) unchanged
    """
    sig = inspect.signature(func)
    old_params = list(sig.parameters.values())

    # Remove 'self' if it's the first parameter
    if old_params and old_params[0].name == "self":
        old_params = old_params[1:]

    new_params = []
    for param in old_params:
        new_annotation = transform_annotation(param.annotation)
        if new_annotation:
            new_params.append(param.replace(annotation=new_annotation))
            continue

        # Handle special FastAPI types by keeping them as-is
        if param.annotation in (Request, Response, BackgroundTasks, UploadFile):
            new_params.append(param)
            continue

        # Leave unchanged
        new_params.append(param)

    # Replace the function's signature with the new parameters
    new_sig = sig.replace(parameters=new_params)
    func.__signature__ = new_sig
    return func


def transform_annotation(annotation: typing.Any) -> Optional[typing.Any]:
    """
    Recursively transform the annotation by replacing custom marker classes
    with FastAPI's Annotated types with appropriate parameters.
    """
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Annotated:
        # Already annotated, no further transformation
        return annotation

    if origin is Union:
        # Handle Union types (e.g., Optional[X] which is Union[X, NoneType])
        transformed_args = tuple(transform_annotation(arg) for arg in args)
        return Union[transformed_args]

    # Handle custom marker classes
    if origin == Param:
        inner_type = args[0]
        return Annotated[inner_type, Path()]
    elif origin == QueryParam:
        inner_type = args[0]
        return Annotated[inner_type, Query()]
    elif origin == HeaderParam:
        inner_type = args[0]
        return Annotated[inner_type, Header()]
    elif origin == BodyParam:
        inner_type = args[0]
        return Annotated[inner_type, Body()]
    elif origin == CookieParam:
        inner_type = args[0]
        return Annotated[inner_type, Cookie()]
    elif origin == FormParam:
        inner_type = args[0]
        return Annotated[inner_type, Form()]
    elif origin == FileParam:
        inner_type = args[0]
        return Annotated[inner_type, File()]
    if annotation is BackgroundTasksParam:  # or if origin == BackgroundTasksParam
        return BackgroundTasks
    else:
        # Not a custom marker, return None to indicate no transformation
        return None
