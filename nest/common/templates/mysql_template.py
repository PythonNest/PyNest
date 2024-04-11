from abc import ABC

from nest.common.templates import Database
from nest.common.templates.orm_template import AsyncORMTemplate, ORMTemplate


class MySQLTemplate(ORMTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(
            module_name=module_name,
            db_type=Database.MYSQL,
        )

    def config_file(self):
        return """from nest.core.database.orm_provider import OrmProvider
import os
from dotenv import load_dotenv

load_dotenv()

config = OrmProvider(
    db_type="mysql",
    config_params=dict(
        host=os.getenv("MYSQL_HOST"),
        db_name=os.getenv("MYSQL_DB_NAME"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        port=int(os.getenv("MYSQL_PORT")),
    )
)
"""

    def requirements_file(self):
        return f"""pynest-api=={self.version}
mysql-connector-python==8.2.0
"""


class AsyncMySQLTemplate(AsyncORMTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(
            module_name=module_name,
            db_type=Database.MYSQL,
        )

    def config_file(self):
        return """from nest.core.database.orm_provider import AsyncOrmProvider
import os
from dotenv import load_dotenv
    
load_dotenv()
    
config = AsyncOrmProvider(
    db_type="mysql",
    config_params=dict(
        host=os.getenv("MYSQL_HOST"),
        db_name=os.getenv("MYSQL_DB_NAME"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        port=int(os.getenv("MYSQL_PORT")),
    )
)
"""

    def requirements_file(self):
        return f"""pynest-api=={self.version}
aiomysql==0.2.0
"""
