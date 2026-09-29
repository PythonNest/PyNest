import click

from nest import __version__
from nest.cli.src.generate.generate_model import SharedOptions
from nest.cli.src.generate.generate_service import GenerateService
from nest.cli.src.generate.generation_result import GenerationPresenter
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
        json: SharedOptions.JSON,
        dry_run: SharedOptions.DRY_RUN,
        force: SharedOptions.FORCE,
    ):
        result = self.generate_service.generate_add_component(
            "resource", name, path=path, dry_run=dry_run, force=force
        )
        self._emit_result(result, json)

    @CliCommand("controller", help="Generate a new nest controller")
    def generate_controller(
        self,
        name: SharedOptions.NAME,
        path: SharedOptions.PATH,
        json: SharedOptions.JSON,
        dry_run: SharedOptions.DRY_RUN,
        force: SharedOptions.FORCE,
    ):
        result = self.generate_service.generate_add_component(
            "controller", name, path=path, dry_run=dry_run, force=force
        )
        self._emit_result(result, json)

    @CliCommand("service", help="Generate a new nest service")
    def generate_service(
        self,
        name: SharedOptions.NAME,
        path: SharedOptions.PATH,
        json: SharedOptions.JSON,
        dry_run: SharedOptions.DRY_RUN,
        force: SharedOptions.FORCE,
    ):
        result = self.generate_service.generate_add_component(
            "service", name, path=path, dry_run=dry_run, force=force
        )
        self._emit_result(result, json)

    @CliCommand("gateway", help="Generate a new nest WebSocket gateway")
    def generate_gateway(
        self,
        name: SharedOptions.NAME,
        path: SharedOptions.PATH,
        json: SharedOptions.JSON,
        dry_run: SharedOptions.DRY_RUN,
        force: SharedOptions.FORCE,
    ):
        result = self.generate_service.generate_add_component(
            "gateway", name, path=path, dry_run=dry_run, force=force
        )
        self._emit_result(result, json)

    @CliCommand("module", help="Generate a new nest module")
    def generate_module(
        self,
        name: SharedOptions.NAME,
        json: SharedOptions.JSON,
        dry_run: SharedOptions.DRY_RUN,
        force: SharedOptions.FORCE,
    ):
        result = self.generate_service.generate_add_component(
            "module", name, dry_run=dry_run, force=force
        )
        self._emit_result(result, json)

    @CliCommand("application", help="Generate a new nest application")
    def generate_app(
        self,
        app_name: SharedOptions.APP_NAME,
        db_type: SharedOptions.DB_TYPE,
        is_async: SharedOptions.IS_ASYNC,
        is_cli: SharedOptions.IS_CLI,
        package_manager: SharedOptions.PACKAGE_MANAGER,
        json: SharedOptions.JSON,
        dry_run: SharedOptions.DRY_RUN,
        force: SharedOptions.FORCE,
    ):
        preset = "cli" if is_cli else "api"
        result = self.generate_service.generate_new_app(
            app_name=app_name,
            preset=preset,
            database=db_type or "none",
            is_async=is_async,
            package_manager=package_manager,
            dry_run=dry_run,
            force=force,
        )
        self._emit_result(result, json)

    @staticmethod
    def _emit_result(result, json_output: bool):
        if json_output:
            click.echo(GenerationPresenter.render_json(result))
        else:
            click.echo(
                GenerationPresenter.render_human(result, version=__version__),
                nl=False,
            )
        if result.error:
            raise click.exceptions.Exit(1)
