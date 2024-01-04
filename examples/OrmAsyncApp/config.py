from nest.core.database.orm_provider import AsyncOrmProvider
import os
from dotenv import load_dotenv

load_dotenv()

config = AsyncOrmProvider(
    db_type="sqlite",
    config_params=dict(
        db_name=os.getenv("SQLITE_DB_NAME", "default_nest_db"),
    )
)
