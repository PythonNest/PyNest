import click

from nest.core import PyNestFactory


class CLIAppFactory(PyNestFactory):
    def __init__(self):
        super().__init__()

    def create(self, module, description="", title="", version="", debug=False):
        app = super().create(
            module,
            is_cli=True,
            description=description,
            title=title,
            version=version,
            debug=debug,
        )
        cli_app = click.Group("main")

        for module in app.modules.values():
            for controller in module.controllers.values():
                cli_app.add_command(controller._cli_group)
        return cli_app
