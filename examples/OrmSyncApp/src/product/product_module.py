from .product_controller import ProductController
from .product_service import ProductService


class ProductModule:
    def __init__(self):
        self.controllers = [ProductController]
        self.providers = [ProductService]
