import asyncio

import click

from nest.core.pynest_container import PyNestContainer
from nest.core.pynest_factory import AbstractPyNestFactory, ModuleType


class CLIAppFactory(AbstractPyNestFactory):
    def __init__(self):
        super().__init__()

    def create(self, app_module: ModuleType, **kwargs):
        container = PyNestContainer()
        container.add_module(app_module)

        cli_app = click.Group("main")
        for module in container.modules.values():
            for controller in module.controllers.values():
                for command in controller._cli_group.commands.values():
                    original_callback = command.callback
                    if asyncio.iscoroutinefunction(original_callback):
                        command.callback = self._run_async(original_callback)
                cli_app.add_command(controller._cli_group)
        return cli_app

    @staticmethod
    def _run_async(coro):
        def wrapper(*args, **kwargs):
            return asyncio.run(coro(*args, **kwargs))

        return wrapper
