import os

from dotenv import load_dotenv

from nest.core.database.odm_provider import OdmProvider

from .example.example_entity import Example
from .product.product_entity import Product
from .user.user_entity import User

load_dotenv()
config = OdmProvider(
    config_params={
        "db_name": os.getenv("DB_NAME", "default_nest_db"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", 27017),
    },
    document_models=[User, Product, Example],
)
