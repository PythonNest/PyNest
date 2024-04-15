from injector import inject

from nest.common.constants import DEPENDENCIES, INJECTABLE_NAME, INJECTABLE_TOKEN
from nest.core.decorators.utils import get_instance_variables, parse_dependencies


def Injectable(cls: str = None):
    def __init__(self, *args, **kwargs):
        ...

    if "__init__" in cls.__dict__:
        pass
    else:
        cls.__init__ = __init__

    dependencies = parse_dependencies(cls)

    setattr(cls, DEPENDENCIES, dependencies)

    setattr(cls, INJECTABLE_TOKEN, True)
    setattr(cls, INJECTABLE_NAME, cls.__name__)

    inject(cls)

    return cls
