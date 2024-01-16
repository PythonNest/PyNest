from .product_service import ProductService
from .product_controller import ProductController


class ProductModule:
    def __init__(self):
        self.providers = [ProductService]
        self.controllers = [ProductController]
