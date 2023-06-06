import click
from nest.cli.click_handlers import create_nest_app, create_nest_module


@click.group()
def nest_cli() -> None:
    pass


@nest_cli.command(
    name="create-nest-app", help="Create a new nest app.",
)
@click.option(
    "--app-name", "-n", help="The name of the nest app.", required=True, type=str,
)
@click.option(
    "--db-type",
    "-db",
    help="The type of the database (postgresql, mysql, sqlite).",
    required=False,
    default="sqlite",
    type=str,
)
def create_nest_app_command(app_name: str, db_type: str = "sqlite"):
    create_nest_app(app_name, db_type)


@nest_cli.command(
    name="generate-module",
    help="Generate a new module (controller, service, entity, model, module).",
)
@click.option(
    "--name", "-n", help="The name of the module.", required=True, type=str,
)
def generate_module(name: str):
    create_nest_module(name=name)


if __name__ == "__main__":
    nest_cli()
