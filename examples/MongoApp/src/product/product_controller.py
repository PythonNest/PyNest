from nest.core import Controller, Depends, Get, Post

from .product_model import Product
from .product_service import ProductService


@Controller("product")
class ProductController:
    def __init__(self, service: ProductService):
        self.service = service

    @Get("/")
    async def get_product(self):
        return await self.service.get_product()

    @Post("/")
    async def add_product(self, product: Product):
        return await self.service.add_product(product)
