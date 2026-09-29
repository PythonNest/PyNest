from typing import Optional

import click

from nest import __version__
from nest.cli.src.generate.generate_service import GenerateService
from nest.cli.src.generate.generation_result import GenerationPresenter


def register_generation_commands(cli_group: click.Group) -> click.Group:
    cli_group.add_command(new_command)
    cli_group.add_command(add_group)
    cli_group.add_command(doctor_command)
    return cli_group


@click.command(name="new", help="Create a new PyNest application")
@click.argument("app_name", required=False)
@click.option("--preset", type=click.Choice(["api", "cli"]), default=None)
@click.option(
    "--database",
    "--db-type",
    type=str,
    default=None,
    help="Database integration: none, sqlite, postgresql, mysql, mongodb.",
)
@click.option("--async", "is_async", is_flag=True, help="Use async database access.")
@click.option(
    "--path",
    "target_path",
    type=click.Path(file_okay=False, dir_okay=True, path_type=str),
    default=None,
)
@click.option(
    "--package-manager",
    type=click.Choice(["requirements", "uv"]),
    default="uv",
    show_default=True,
)
@click.option("--prompt", is_flag=True, help="Force guided prompts.")
@click.option("--yes", is_flag=True, help="Accept defaults and do not ask questions.")
@click.option("--dry-run", is_flag=True, help="Show the generation plan only.")
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--quiet", is_flag=True, help="Only print essential information.")
@click.option("--force", is_flag=True, help="Overwrite supported existing files.")
def new_command(
    app_name: Optional[str],
    preset: Optional[str],
    database: Optional[str],
    is_async: bool,
    target_path: Optional[str],
    package_manager: str,
    prompt: bool,
    yes: bool,
    dry_run: bool,
    json_output: bool,
    quiet: bool,
    force: bool,
):
    should_prompt = _should_prompt(app_name, prompt, yes, json_output)
    if should_prompt:
        app_name = app_name or click.prompt("Application name", type=str)
        preset = _prompt_preset(preset)
        database = _prompt_database(database)
        if database in ("postgresql", "mysql", "sqlite") and not is_async:
            is_async = click.confirm("Use async database access?", default=False)
        package_manager = _prompt_package_manager(package_manager)

    result = GenerateService().generate_new_app(
        app_name=app_name,
        preset=preset or "api",
        database=database or "none",
        is_async=is_async,
        path=target_path,
        package_manager=package_manager,
        dry_run=dry_run,
        force=force,
    )
    _emit_result(result, json_output=json_output, quiet=quiet)


def _should_prompt(
    app_name: Optional[str], prompt: bool, yes: bool, json_output: bool
) -> bool:
    if prompt:
        return True
    if yes or json_output:
        return False
    return app_name is None and click.get_text_stream("stdin").isatty()


def _prompt_preset(current: Optional[str]) -> str:
    if current:
        return current
    click.echo("Preset:")
    click.echo("  1. HTTP API")
    click.echo("  2. CLI application")
    choice = click.prompt(
        "Choose preset",
        default="1",
        type=click.Choice(["1", "2"]),
        show_choices=False,
    )
    return {"1": "api", "2": "cli"}[choice]


def _prompt_database(current: Optional[str]) -> str:
    if current:
        return current
    click.echo("Database:")
    click.echo("  1. None")
    click.echo("  2. SQLite")
    click.echo("  3. PostgreSQL")
    click.echo("  4. MySQL")
    click.echo("  5. MongoDB")
    choice = click.prompt(
        "Choose database",
        default="1",
        type=click.Choice(["1", "2", "3", "4", "5"]),
        show_choices=False,
    )
    return {
        "1": "none",
        "2": "sqlite",
        "3": "postgresql",
        "4": "mysql",
        "5": "mongodb",
    }[choice]


def _prompt_package_manager(current: Optional[str]) -> str:
    if current and current != "uv":
        return current
    click.echo("Package manager:")
    click.echo("  1. uv")
    click.echo("  2. requirements.txt")
    choice = click.prompt(
        "Choose package manager",
        default="1",
        type=click.Choice(["1", "2"]),
        show_choices=False,
    )
    return {"1": "uv", "2": "requirements"}[choice]


def _emit_result(result, json_output: bool, quiet: bool = False):
    if json_output:
        click.echo(GenerationPresenter.render_json(result))
    elif not quiet:
        click.echo(
            GenerationPresenter.render_human(result, version=__version__),
            nl=False,
        )
    if result.error:
        raise click.exceptions.Exit(1)


@click.group(name="add", help="Add code to an existing PyNest application")
def add_group():
    pass


def _add_component_command(component_type: str):
    @click.command(name=component_type, help=f"Add a PyNest {component_type}")
    @click.argument("name")
    @click.option(
        "--path",
        "target_path",
        type=click.Path(file_okay=False, dir_okay=True, path_type=str),
        default=None,
    )
    @click.option("--dry-run", is_flag=True, help="Show the generation plan only.")
    @click.option(
        "--json", "json_output", is_flag=True, help="Emit machine-readable JSON."
    )
    @click.option("--quiet", is_flag=True, help="Only print essential information.")
    @click.option("--force", is_flag=True, help="Overwrite supported existing files.")
    def command(
        name: str,
        target_path: Optional[str],
        dry_run: bool,
        json_output: bool,
        quiet: bool,
        force: bool,
    ):
        result = GenerateService().generate_add_component(
            component_type=component_type,
            name=name,
            path=target_path,
            dry_run=dry_run,
            force=force,
        )
        _emit_result(result, json_output=json_output, quiet=quiet)

    return command


for _component_type in ("resource", "module", "controller", "service", "gateway"):
    add_group.add_command(_add_component_command(_component_type))


@click.command(name="doctor", help="Check the current PyNest project")
@click.option(
    "--path",
    "target_path",
    type=click.Path(file_okay=False, dir_okay=True, path_type=str),
    default=None,
)
@click.option("--json", "json_output", is_flag=True, help="Emit machine-readable JSON.")
@click.option("--quiet", is_flag=True, help="Only print essential information.")
def doctor_command(target_path: Optional[str], json_output: bool, quiet: bool):
    result = GenerateService().doctor_project(path=target_path)
    _emit_result(result, json_output=json_output, quiet=quiet)
