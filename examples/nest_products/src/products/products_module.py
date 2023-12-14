from .products_controller import ProductsController
from .products_service import ProductsService


class ProductsModule:
    def __init__(self):
        self.providers = [ProductsService]
        self.controllers = [ProductsController]
