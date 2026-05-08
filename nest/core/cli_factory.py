import asyncio
import inspect
from functools import partial

import click

from nest.core.pynest_container import PyNestContainer
from nest.core.pynest_factory import AbstractPyNestFactory, ModuleType


class CLIAppFactory(AbstractPyNestFactory):
    def __init__(self):
        super().__init__()

    def create(self, app_module: ModuleType, **kwargs):
        container = PyNestContainer()
        container.add_module(app_module)
        container.build()

        cli_app = click.Group("main")
        for module in container.modules.values():
            for controller_class in module.compiled.controllers:
                if not hasattr(controller_class, "_cli_group"):
                    continue
                instance = self._resolve_instance(controller_class, container)
                cli_group = self._build_cli_group(controller_class, instance)
                cli_app.add_command(cli_group)
        return cli_app

    @staticmethod
    def _resolve_instance(controller_class: type, container: PyNestContainer):
        """Instantiate a CLI controller by resolving its __init__ deps from the container."""
        sig = inspect.signature(controller_class.__init__)
        params = list(sig.parameters.values())[1:]  # drop self
        kwargs = {}
        for param in params:
            if param.annotation is not inspect.Parameter.empty:
                kwargs[param.name] = container.get(param.annotation)
        return controller_class(**kwargs)

    def _build_cli_group(self, controller_class: type, instance) -> click.Group:
        original_group = controller_class._cli_group
        new_group = click.Group(original_group.name)
        for cmd_name, cmd in original_group.commands.items():
            # cmd.callback was set to partial(unbound_method, controller_class)
            # Re-bind to the resolved instance so __init__ injected attrs are accessible.
            unbound = cmd.callback.func if hasattr(cmd.callback, "func") else cmd.callback
            bound_callback = partial(unbound, instance)
            if asyncio.iscoroutinefunction(unbound):
                bound_callback = self._run_async(bound_callback)
            new_cmd = click.Command(
                name=cmd_name,
                callback=bound_callback,
                params=list(cmd.params),
                help=cmd.help,
            )
            new_group.add_command(new_cmd)
        return new_group

    @staticmethod
    def _run_async(coro):
        def wrapper(*args, **kwargs):
            return asyncio.run(coro(*args, **kwargs))

        return wrapper
