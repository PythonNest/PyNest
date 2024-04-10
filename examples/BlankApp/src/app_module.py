from fastapi import FastAPI

from nest.core import Module, PyNestFactory

from .app_controller import AppController
from .app_service import AppService
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


app = PyNestFactory.create(
    AppModule,
    description="This is my FastAPI app.",
    title="My App",
    version="1.0.0",
    debug=True,
)

http_server: FastAPI = app.get_server()
