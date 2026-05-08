import inspect
from typing import Callable, List

import click


def parse_params(func: Callable) -> List[click.Option]:
    """Used by the CLI layer — parses Click options from function annotations."""
    signature = inspect.signature(func)
    params = []
    for param in signature.parameters.values():
        try:
            if param.annotation != param.empty:
                params.append(param.annotation)
        except Exception as e:
            raise e
    return params
