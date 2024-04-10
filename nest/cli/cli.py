from typing import Optional

import click

from nest.cli.click_handlers import create_nest_app, create_nest_module

### Options ###
APP_NAME = click.option(
    "--app-name",  # Changed the underscore to a hyphen for consistency
    "-n",
    help="The name of the nest app.",
    required=True,
    type=str,
    default=".",
)

DB_TYPE = click.option(
    "--db-type",
    "-db",
    help="The type of the database (postgresql, mysql, sqlite, or mongo db).",
    required=False,
    default=None,
    type=str,
)

MODULE_NAME = click.option(
    "--name",
    "-n",
    help="The name of the module.",
    required=False,
    type=str,
)

IS_ASYNC = click.option(
    "--is-async",  # Changed the underscore to a hyphen for consistency
    help="Whether the project should be async or not (only for relational databases).",
    required=False,
    is_flag=True,
)


@click.group()
def nest_cli() -> None:
    pass


@nest_cli.command(
    name="create-nest-app",
    help="Create a new nest app.",
)
@APP_NAME
@DB_TYPE
@IS_ASYNC
def create_nest_app_command(
    app_name: str = ".", db_type: str = None, is_async: bool = False
):
    print(app_name, db_type, is_async)
    create_nest_app(app_name=app_name, db_type=db_type, is_async=is_async)


# Create a new group for generating boilerplate
@nest_cli.group("g", short_help="Generate boilerplate code.")
def generate():
    pass


@generate.command(
    name="module",
    help="Generate a new module (controller, service, entity, model, module).",
)
@MODULE_NAME
def generate_module(name: str):
    create_nest_module(name=name)
