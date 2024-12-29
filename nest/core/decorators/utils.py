import ast
import inspect
from typing import Callable, List, Dict, Type

import click

from nest.common.constants import INJECTABLE_TOKEN


def _is_valid_instance_variable(target):
    """
    Checks if the target is a valid instance variable.

    Args:
        target: The AST target node to check.
        dependencies: A list of attribute names to exclude.

    Returns:
        bool: True if the target is a valid instance variable, False otherwise.
    """
    return (
        isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == "self"
    )

def get_instance_variables(cls):
    """
    Retrieves instance variables assigned in the __init__ method of a class,
    excluding those that are injected dependencies.

    Args:
        cls (type): The class to inspect.

    Returns:
        dict: A dictionary with variable names as keys and their assigned values.
    """
    try:
        source = inspect.getsource(cls.__init__).strip()
        tree = ast.parse(source)

        # Getting the parameter names to exclude dependencies
        dependencies: Dict[str, ...] = parse_dependencies(cls, check_parent=True)
        assign_nodes = filter(lambda node: isinstance(node, ast.Assign), ast.walk(tree))
        return {
            # Here you can either store the source code of the value or
            # evaluate it in the class' context, depending on your needs
            target.attr: ast.get_source_segment(source, node.value)
            for node in assign_nodes
            for target in node.targets
            if _is_valid_instance_variable(target)
            and target.attr not in dependencies  # Exclude dependencies
        }
    except Exception:
        return {}


def get_non_dependencies_params(cls: Type):
    source = inspect.getsource(cls.__init__).strip()
    tree = ast.parse(source)
    return {
        node.attr: node.value.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
    }


def _check_injectable_in_object(param: inspect.Parameter) -> bool:
    return (
        param.annotation != param.empty
        and hasattr(param.annotation, "__dict__")
        and INJECTABLE_TOKEN in param.annotation.__dict__
    )

def _check_injectable_in_object_and_parents(param: inspect.Parameter) -> bool:
    return param.annotation != param.empty and getattr(
        param.annotation, INJECTABLE_TOKEN, False
    )

def parse_dependencies(cls: Type, check_parent: bool = False) -> Dict[str, Type]:
    """
    Returns:
        mapping of injectable parameters name to there annotation
    """
    signature = inspect.signature(cls.__init__)
    filter_by = _check_injectable_in_object_and_parents if check_parent else _check_injectable_in_object
    params: List[inspect.Parameter] = filter(filter_by, signature.parameters.values())
    return {
        param.name: param.annotation
        for param in params
    }


def parse_params(func: Callable) -> List[click.Option]:
    """
    Returns:
        all parameters with annotation
    """
    signature = inspect.signature(func)
    return [
        param.annotation
        for param in signature.parameters.values()
        if param.annotation != param.empty
    ]
