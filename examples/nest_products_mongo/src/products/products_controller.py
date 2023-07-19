from nest.core import Depends, Controller, Get, Post
from examples.nest_products_mongo.src.products.products_service import ProductsService
from examples.nest_products_mongo.src.products.products_model import Product


@Controller("products")
class ProductsController:
    service: ProductsService = Depends(ProductsService)

    @Get("/get_products")
    def get_products(self):
        return self.service.get_products()

    @Get("/get_product/{product_id}")
    def get_product(self, product_id: int):
        return self.service.get_product(product_id)

    @Post("/add_product")
    def add_product(self, product: Product):
        return self.service.add_product(product)

    @Get("last_product")
    def last_product(self):
        return self.service.last_product()
