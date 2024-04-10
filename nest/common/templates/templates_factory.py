from typing import Optional, Union

from nest.common.templates import Database
from nest.common.templates.base_template import BaseTemplate
from nest.common.templates.blank_template import BlankTemplate
from nest.common.templates.mongo_template import MongoTemplate
from nest.common.templates.mysql_template import AsyncMySQLTemplate, MySQLTemplate
from nest.common.templates.postgres_template import (
    AsyncPostgresqlTemplate,
    PostgresqlTemplate,
)
from nest.common.templates.sqlite_template import AsyncSQLiteTemplate, SQLiteTemplate


class TemplateFactory:
    @staticmethod
    def get_template(
        db_type: Union[Database, str, None],
        module_name: str,
        is_async: Optional[bool] = False,
    ) -> BaseTemplate:
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
