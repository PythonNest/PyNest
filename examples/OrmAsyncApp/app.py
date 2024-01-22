from config import config
from nest.core import PyNestFactory, Module
from src.example.example_module import ExampleModule
from src.user.user_module import UserModule
from src.product.product_module import ProductModule


@Module(
    imports=[ExampleModule, UserModule, ProductModule], controllers=[], providers=[]
)
class AppModule:
    pass


app = PyNestFactory.create(
    AppModule,
    description="This is my FastAPI app drive by Async ORM Engine",
    title="My App",
    version="1.0.0",
    debug=True,
)

http_server = app.get_server()


@http_server.on_event("startup")
async def startup():
    await config.create_all()
