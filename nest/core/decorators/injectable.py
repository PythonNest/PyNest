from injector import inject

from nest.common.constants import DEPENDENCIES, INJECTABLE_NAME, INJECTABLE_TOKEN
from nest.core.decorators.utils import parse_dependencies


def Injectable(cls=None, *args, **kwargs):
    def decorator(inner_cls):
        if "__init__" not in inner_cls.__dict__:
            def __init__(self, *args, **kwargs):
                ...
            inner_cls.__init__ = __init__
        
        dependencies = parse_dependencies(inner_cls)
        
        setattr(inner_cls, DEPENDENCIES, dependencies)
        setattr(inner_cls, INJECTABLE_TOKEN, True)
        setattr(inner_cls, INJECTABLE_NAME, inner_cls.__name__)
        
        inject(inner_cls)
        
        return inner_cls

    if cls is not None:
        return decorator(cls)
    
    return decorator
