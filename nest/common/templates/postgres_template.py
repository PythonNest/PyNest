from abc import ABC

from nest.common.templates import Database
from nest.common.templates.orm_template import AsyncORMTemplate, ORMTemplate


class PostgresqlTemplate(ORMTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(
            module_name=module_name,
            db_type=Database.POSTGRESQL,
        )

    def config_file(self):
        return """from nest.core.database.orm_provider import OrmProvider
import os
from dotenv import load_dotenv
    
load_dotenv()
    
config = OrmProvider(
    db_type="postgresql",
    config_params=dict(
        host=os.getenv("POSTGRESQL_HOST", "localhost"),
        db_name=os.getenv("POSTGRESQL_DB_NAME", "default_nest_db"),
        user=os.getenv("POSTGRESQL_USER", "postgres"),
        password=os.getenv("POSTGRESQL_PASSWORD", "postgres"),
        port=int(os.getenv("POSTGRESQL_PORT", 5432)),
    )
)
"""

    def requirements_file(self):
        return f"""pynest-api=={self.version}
psycopg2==2.9.6
"""


class AsyncPostgresqlTemplate(AsyncORMTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(
            module_name=module_name,
            db_type=Database.POSTGRESQL,
        )

    def config_file(self):
        return """from nest.core.database.orm_provider import AsyncOrmProvider
import os
from dotenv import load_dotenv
    
load_dotenv()
    
config = AsyncOrmProvider(
    db_type="postgresql",
    config_params=dict(
        host=os.getenv("POSTGRESQL_HOST", "localhost"),
        db_name=os.getenv("POSTGRESQL_DB_NAME", "default_nest_db"),
        user=os.getenv("POSTGRESQL_USER", "postgres"),  
        password=os.getenv("POSTGRESQL_PASSWORD", "postgres"),
        port=int(os.getenv("POSTGRESQL_PORT", 5432)),
    )
)
"""

    def requirements_file(self):
        return f"""pynest-api=={self.version}
asyncpg==0.29.0
"""
