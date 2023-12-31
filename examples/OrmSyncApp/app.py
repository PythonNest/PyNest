from config import config
from nest.core.app import App
from src.example.example_module import ExampleModule
from src.user.user_module import UserModule
from src.product.product_module import ProductModule

app = App(
    description="PyNest service", modules=[ExampleModule, UserModule, ProductModule]
)


@app.on_event("startup")
def startup():
    config.create_all()
