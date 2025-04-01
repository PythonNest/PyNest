from nest.common.constants import STATUS_CODE_TOKEN
from typing import TypeVar, Callable
import sys

if sys.version_info >= (3, 10):
    from typing import ParamSpec, TypeAlias
else:
    from typing_extensions import ParamSpec, TypeAlias

P = ParamSpec("P")
R = TypeVar("R")
Func: TypeAlias = Callable[[P], R]


def HttpCode(status_code: int):
    """
    Decorator that sets the HTTP status code for a route.

    Args:
        status_code (int): The HTTP status code for the response.
    """

    def decorator(func: Func) -> Func:
        if not hasattr(func, STATUS_CODE_TOKEN):
            setattr(func, STATUS_CODE_TOKEN, status_code)
        return func

    return decorator
