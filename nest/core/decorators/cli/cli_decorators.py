from functools import partial

import click

from nest.core.decorators.utils import parse_params


def CliController(name: str, **kwargs):
    def decorator(cls):

        cli_group = click.Group(name, **kwargs)
        setattr(cls, "_cli_group", cli_group)

        for attr_name, method in cls.__dict__.items():
            if callable(method) and hasattr(method, "_cli_command"):
                params = parse_params(method)
                cli_command = click.Command(
                    name=method._cli_command.name,
                    callback=partial(method, cls),
                    params=params,
                )
                cli_group.add_command(cli_command)

        return cls

    return decorator


def CliCommand(name: str, **kwargs):
    def decorator(func):
        params = parse_params(func)
        func._cli_command = click.Command(
            name, callback=func, params=params, help=kwargs.get("help", None)
        )
        return func

    return decorator
