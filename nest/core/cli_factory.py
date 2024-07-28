import click

from nest.core.pynest_factory import AbstractPyNestFactory, ModuleType
from nest.core.pynest_container import PyNestContainer


class CLIAppFactory(AbstractPyNestFactory):
    def __init__(self):
        super().__init__()

    def create(self, app_module: ModuleType, **kwargs):
        container = PyNestContainer()
        container.add_module(app_module)

        cli_app = click.Group("main")

        for module in container.modules.values():
            for controller in module.controllers.values():
                cli_app.add_command(controller._cli_group)
        return cli_app
