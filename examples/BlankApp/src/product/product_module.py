from nest.core import Module

from .product_controller import ProductController
from .product_service import ProductService


@Module(controllers=[ProductController], providers=[ProductService], imports=[])
class ProductModule:
    pass
