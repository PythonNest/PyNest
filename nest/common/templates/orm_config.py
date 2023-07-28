def generate_orm_config(db_type: str):
    if db_type == "mongodb":
        service_import = "from nest.core.database.base_odm import OdmService\n" \
                         "from src.examples.examples_entity import Examples"
    else:
        service_import = "from nest.core.database.base_orm import OrmService"

    base_template = f"""{service_import}
import os
from dotenv import load_dotenv

load_dotenv()
    """

    if db_type == "sqlite":
        return f"""{base_template}
config = OrmService(
    db_type="{db_type}",
    config_params=dict(
        db_name=os.getenv("SQLITE_DB_NAME", "default_nest_db"),
    )
)
        """
    elif db_type == "postgresql":
        return f"""{base_template}
config = OrmService(
    db_type="{db_type}",
    config_params=dict(
        host=os.getenv("POSTGRESQL_HOST"),
        db_name=os.getenv("POSTGRESQL_DB_NAME"),
        user=os.getenv("POSTGRESQL_USER"),
        password=os.getenv("POSTGRESQL_PASSWORD"),
        port=int(os.getenv("POSTGRESQL_PORT")),
    )
)
        """
    elif db_type == "mysql":
        return f"""{base_template}
config = OrmService(
    db_type="{db_type}",
    config_params=dict(
        host=os.getenv("MYSQL_HOST"),
        db_name=os.getenv("MYSQL_DB_NAME"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        port=int(os.getenv("MYSQL_PORT")),
    )
)
        """
    elif db_type == "mongodb":
        return f"""{base_template}

config = OdmService(
    db_type="{db_type}",
    config_params={{
        "db_name": os.getenv("DB_NAME"),
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT"),
    }},
    document_models=[Examples]
)       
        """
    else:
        raise ValueError(f"Unsupported db type: {db_type}")
