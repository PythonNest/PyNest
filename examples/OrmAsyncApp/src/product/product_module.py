from nest.core import Module
from .product_service import ProductService
from .product_controller import ProductController


@Module(controllers=[ProductController], providers=[ProductService], imports=[])
class ProductModule:
    pass
