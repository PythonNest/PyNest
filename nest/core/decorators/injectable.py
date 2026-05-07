from __future__ import annotations

from typing import Callable, Optional, Type, Union

from injector import inject

from nest.common.constants import INJECTABLE_TOKEN
from nest.common.provider import Scope


def Injectable(
    target_class: Optional[Type] = None,
    *,
    scope: Scope = Scope.SINGLETON,
) -> Union[Type, Callable]:
    """
    Mark a class as injectable so the PyNest container can wire its dependencies.

    Usage:
        @Injectable
        class MyService: ...

        @Injectable(scope=Scope.TRANSIENT)
        class MyService: ...
    """

    def decorator(cls: Type) -> Type:
        # Apply injector's @inject so constructor params are resolved by type annotation.
        # Only apply when the class defines its own __init__ with annotated parameters,
        # to avoid failures on Python 3.14+ for classes with no custom __init__.
        own_init = cls.__dict__.get("__init__")
        if own_init is not None and getattr(own_init, "__annotations__", None):
            inject(cls)

        # Store metadata flags — never set dependency values as class attributes
        setattr(cls, INJECTABLE_TOKEN, True)
        setattr(cls, "__injectable_scope__", scope)
        setattr(cls, "__injectable_name__", cls.__name__)

        return cls

    if target_class is not None:
        # Called as @Injectable (no parentheses)
        return decorator(target_class)

    # Called as @Injectable(scope=...) with arguments
    return decorator
