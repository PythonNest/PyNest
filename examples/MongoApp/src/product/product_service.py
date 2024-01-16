from .product_model import Product
from .product_entity import Product as ProductEntity
from nest.core.decorators import db_request_handler
from functools import lru_cache


@lru_cache()
class ProductService:
    @db_request_handler
    async def add_product(self, product: Product):
        new_product = ProductEntity(**product.dict())
        await new_product.save()
        return new_product.id

    @db_request_handler
    async def get_product(self):
        return await ProductEntity.find_all().to_list()
