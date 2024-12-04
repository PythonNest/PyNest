from nest.core import Module
from nest.web import PyNestWebFactory

from .app_controller import AppController
from .app_service import AppService
from .config import config
from .example.example_module import ExampleModule
from .product.product_module import ProductModule
from .user.user_module import UserModule


@Module(
    imports=[ExampleModule, UserModule, ProductModule],
    controllers=[AppController],
    providers=[AppService],
)
class AppModule:
    pass


app = PyNestWebFactory.create(
    AppModule,
    description="This is my FastAPI app drive by Sync ORM Engine",
    title="My App",
    version="1.0.0",
    debug=True,
)

http_server = app.get_server()


@http_server.on_event("startup")
def startup():
    config.create_all()
