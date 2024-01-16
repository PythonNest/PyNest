from nest.core import Controller, Get, Post, Depends
from .product_service import ProductService
from .product_model import Product


@Controller("product")
class ProductController:

    service: ProductService = Depends(ProductService)

    @Get("/")
    def get_product(self):
        return self.service.get_product()

    @Post("/")
    def add_product(self, product: Product):
        return self.service.add_product(product)
