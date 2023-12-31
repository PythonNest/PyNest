from config import config
from nest.core.app import App
from src.product.product_module import ProductModule
from src.user.user_module import UserModule
from src.example.example_module import ExampleModule

app = App(
    description="PyNest service", modules=[ProductModule, UserModule, ExampleModule]
)


@app.on_event("startup")
async def startup():
    await config.create_all()
