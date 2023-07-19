from nest.core import OdmService
import os
from dotenv import load_dotenv

load_dotenv()

config = OdmService(
    db_type="mongodb",
    config_params=dict(
        host=os.getenv("MONGO_HOST"),
        db_name=os.getenv("MONGO_DB_NAME"),
        user=os.getenv("MONGO_USER"),
        password=os.getenv("MONGO_PASSWORD"),
        port=int(os.getenv("MONGO_PORT")),
        srv=os.getenv("MONGO_SRV", True),
    ),
    document_models=[]
)
