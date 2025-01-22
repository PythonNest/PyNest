from typing import Annotated, Callable

from fastapi import Path, Query, Header, Body, File, UploadFile, Response, Request, BackgroundTasks, Form
from nest.core.protocols import Param, Query as QueryParam, Header as HeaderParam, Body as BodyParam, \
    Cookie as CookieParam, File as FileParam, Form as FormParam
import functools
import inspect
import typing


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
    A function that modifies the signature to remove "self"
    and convert Param/Query/Header/Body to FastAPI’s annotated params.
    """
    sig = inspect.signature(func)
    new_params = []

    old_parameters = list(sig.parameters.values())

    # 1) If the first param is named 'self', skip it entirely from the new signature
    #    (because we have a BOUND method).
    if old_parameters and old_parameters[0].name == "self":
        old_parameters = old_parameters[1:]

    for param in old_parameters:
        annotation = param.annotation

        if typing.get_origin(annotation) == Param:
            inner_type = typing.get_args(annotation)[0]
            new_annotation = Annotated[inner_type, Path()]
            new_params.append(param.replace(annotation=new_annotation))

        elif typing.get_origin(annotation) == QueryParam:
            inner_type = typing.get_args(annotation)[0]
            new_annotation = Annotated[inner_type, Query()]
            new_params.append(param.replace(annotation=new_annotation))

        elif typing.get_origin(annotation) == HeaderParam:
            inner_type = typing.get_args(annotation)[0]
            new_annotation = Annotated[inner_type, Header()]
            new_params.append(param.replace(annotation=new_annotation))

        elif typing.get_origin(annotation) == BodyParam:
            inner_type = typing.get_args(annotation)[0]
            new_annotation = Annotated[inner_type, Body()]
            new_params.append(param.replace(annotation=new_annotation))
        else:
            # unchanged param
            new_params.append(param)

    new_sig = sig.replace(parameters=new_params)
    func.__signature__ = new_sig
    return func
