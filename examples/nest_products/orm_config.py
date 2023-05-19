from nest.core import OrmService
import os
from dotenv import load_dotenv

load_dotenv()

config = OrmService(
    db_type="postgresql",
    config_params=dict(
        host=os.getenv("POSTGRESQL_HOST"),
        db_name=os.getenv("POSTGRESQL_DB_NAME"),
        user=os.getenv("POSTGRESQL_USER"),
        password=os.getenv("POSTGRESQL_PASSWORD"),
        port=int(os.getenv("POSTGRESQL_PORT")),
    )
)
