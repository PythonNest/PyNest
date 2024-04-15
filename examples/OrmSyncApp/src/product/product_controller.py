from nest.core import Controller, Depends, Get, Post

from .product_model import Product
from .product_service import ProductService


@Controller("product")
class ProductController:
    def __init__(self, service: ProductService):
        self.service = service

    @Get("/")
    def get_products(self):
        return self.service.get_products()

    @Post("/")
    def add_product(self, product: Product):
        return self.service.add_product(product)
