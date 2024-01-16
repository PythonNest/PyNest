from nest.core import PyNestFactory, Module
from src.example.example_module import ExampleModule
from src.user.user_module import UserModule
from src.product.product_module import ProductModule
from fastapi import FastAPI


@Module(imports=[ExampleModule, UserModule, ProductModule])
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
