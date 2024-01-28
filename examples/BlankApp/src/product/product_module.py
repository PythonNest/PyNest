from .product_controller import ProductController
from .product_service import ProductService
from nest.core import Module


@Module(controllers=[ProductController], providers=[ProductService], imports=[])
class ProductModule:
    pass
