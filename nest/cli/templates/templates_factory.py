from typing import Optional, Union

from nest.cli.templates import Database
from nest.cli.templates.base_template import BaseTemplate
from nest.cli.templates.blank_template import BlankTemplate
from nest.cli.templates.cli_templates import ClickTemplate
from nest.cli.templates.mongo_template import MongoTemplate
from nest.cli.templates.mysql_template import AsyncMySQLTemplate, MySQLTemplate
from nest.cli.templates.postgres_template import (
    AsyncPostgresqlTemplate,
    PostgresqlTemplate,
)
from nest.cli.templates.sqlite_template import AsyncSQLiteTemplate, SQLiteTemplate


class TemplateFactory:
    @staticmethod
    def get_template(
        db_type: Union[Database, str, None],
        module_name: str,
        is_async: Optional[bool] = False,
        is_cli: Optional[bool] = False,
    ) -> BaseTemplate:
        if is_cli:
            return ClickTemplate(module_name=module_name)
        if not db_type:
            return BlankTemplate(module_name=module_name)
        elif db_type == Database.POSTGRESQL.value:
            if is_async:
                return AsyncPostgresqlTemplate(module_name=module_name)
            else:
                return PostgresqlTemplate(module_name=module_name)
        elif db_type == Database.MYSQL.value:
            if is_async:
                return AsyncMySQLTemplate(module_name=module_name)
            else:
                return MySQLTemplate(module_name=module_name)
        elif db_type == Database.SQLITE.value:
            if is_async:
                return AsyncSQLiteTemplate(module_name=module_name)
            else:
                return SQLiteTemplate(module_name=module_name)
        elif db_type == Database.MONGODB.value:
            return MongoTemplate(module_name=module_name)
        else:
            raise ValueError(f"Unknown database type: {db_type}")
