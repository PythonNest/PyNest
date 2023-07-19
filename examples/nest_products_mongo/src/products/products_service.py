from examples.nest_products_mongo.src.products.products_model import Product
from examples.nest_products_mongo.src.products.products_entity import Product as ProductEntity
from nest.core.decorators import db_request_handler


class ProductsService:

    @db_request_handler
    def add_product(self, product: Product):
        product_entity = ProductEntity(
            name=product.name, price=product.price, description=product.description
        )
        product_entity.save()
        return product_entity.id

    @db_request_handler
    def get_products(self):
        return ProductEntity.find_all()

    @db_request_handler
    def get_product(self, product_id: int):
        return ProductEntity.find_one({"_id": product_id})

    @db_request_handler
    def last_product(self):
        return ProductEntity.find_one(sort=[("_id", -1)])
