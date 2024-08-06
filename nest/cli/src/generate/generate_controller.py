import click
from click import Option

from nest.cli.src.generate.generate_model import SharedOptions
from nest.cli.src.generate.generate_service import GenerateService
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController


@CliController("generate")
class GenerateController:
    def __init__(self, generate_service: GenerateService):
        self.generate_service = generate_service

    @CliCommand("resource")
    def generate_resource(
        self,
        name: SharedOptions.NAME,
        path: SharedOptions.PATH,
    ):
        self.generate_service.generate_resource(name, path)

    @CliCommand("controller", help="Generate a new nest controller")
    def generate_controller(self, name: SharedOptions.NAME, path: SharedOptions.PATH):
        self.generate_service.generate_controller(name, path)

    @CliCommand("service", help="Generate a new nest service")
    def generate_service(self, name: SharedOptions.NAME, path: SharedOptions.PATH):
        self.generate_service.generate_service(name, path)

    @CliCommand("module", help="Generate a new nest module")
    def generate_module(self, name: SharedOptions.NAME):
        self.generate_service.generate_module(name)

    @CliCommand("application", help="Generate a new nest application")
    def generate_app(
        self,
        app_name: SharedOptions.APP_NAME,
        db_type: SharedOptions.DB_TYPE,
        is_async: SharedOptions.IS_ASYNC,
        is_cli: SharedOptions.IS_CLI,
    ):
        click.echo(f"Generating app {app_name}")
        self.generate_service.generate_app(app_name, db_type, is_async, is_cli)
