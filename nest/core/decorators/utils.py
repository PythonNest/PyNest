import ast
import inspect

from nest.common.constants import INJECTABLE_TOKEN


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
        dependencies = set(
            param.name
            for param in inspect.signature(cls.__init__).parameters.values()
            if param.annotation != param.empty
            and getattr(param.annotation, "__injectable__", False)
        )

        instance_vars = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Attribute)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "self"
                    ):
                        # Exclude dependencies
                        if target.attr not in dependencies:
                            # Here you can either store the source code of the value or
                            # evaluate it in the class' context, depending on your needs
                            instance_vars[target.attr] = ast.get_source_segment(
                                source, node.value
                            )
        return instance_vars
    except Exception as e:
        return {}


def get_non_dependencies_params(cls):
    source = inspect.getsource(cls.__init__).strip()
    tree = ast.parse(source)
    non_dependencies = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            non_dependencies[node.attr] = node.value.id
    return non_dependencies


def parse_dependencies(cls):
    signature = inspect.signature(cls.__init__)
    dependecies = {}
    for param in signature.parameters.values():
        try:
            if (
                param.annotation != param.empty
                and hasattr(param.annotation, "__dict__")
                and INJECTABLE_TOKEN in param.annotation.__dict__
            ):
                dependecies[param.name] = param.annotation
        except Exception as e:
            raise e
    return dependecies
