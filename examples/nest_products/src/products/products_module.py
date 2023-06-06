from examples.nest_products.src.products.products_controller import ProductsController
from examples.nest_products.src.products.products_service import ProductsService


class ProductsModule:
    def __init__(self):
        self.providers = [ProductsService]
        self.controllers = [ProductsController]
