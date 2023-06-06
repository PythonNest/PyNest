from orm_config import config
from nest.core import App
from src.users.users_module import UsersModule
from src.products.products_module import ProductsModule
from src.test.test_module import TestModule

app = App(
    description="FastAPI + SQLAlchemy + PostgreSQL",
    modules=[UsersModule, ProductsModule, TestModule],
    init_db=config.create_all(),
)
