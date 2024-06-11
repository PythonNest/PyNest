from injector import inject
from nest.common.constants import DEPENDENCIES, INJECTABLE_NAME, INJECTABLE_TOKEN
from nest.core.decorators.utils import parse_dependencies
from typing import Type, Optional, Callable


def Injectable(target_class: Optional[Type] = None, *args, **kwargs) -> Callable:
    """
    Decorator to mark a class as injectable and handle its dependencies.

    Args:
        target_class (Type, optional): The class to be decorated.

    Returns:
        Callable: The decorator function.
    """

    def decorator(decorated_class: Type) -> Type:
        """
        Inner decorator function to process the class.

        Args:
            decorated_class (Type): The class to be processed.

        Returns:
            Type: The processed class with dependencies injected.
        """

        if "__init__" not in decorated_class.__dict__:

            def init_method(self, *args, **kwargs):
                pass

            decorated_class.__init__ = init_method

        dependencies = parse_dependencies(decorated_class)

        setattr(decorated_class, DEPENDENCIES, dependencies)
        setattr(decorated_class, INJECTABLE_TOKEN, True)
        setattr(decorated_class, INJECTABLE_NAME, decorated_class.__name__)

        inject(decorated_class)

        return decorated_class

    if target_class is not None:
        return decorator(target_class)

    return decorator
