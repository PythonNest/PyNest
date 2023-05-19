from examples.nest_products.src.products.products_model import Product
from examples.nest_products.src.products.products_entity import Product as ProductEntity
from examples.nest_products.orm_config import config
from nest.core.decorators import db_request_handler


class ProductsService:
    def __init__(self):
        self.config = config
        self.session = self.config.get_db()

    @db_request_handler
    def add_product(self, product: Product):
        product_entity = ProductEntity(
            name=product.name,
            price=product.price,
            description=product.description
        )
        self.session.add(product_entity)
        self.session.commit()
        return product_entity.id

    @db_request_handler
    def get_products(self):
        return self.session.query(ProductEntity).all()

    @db_request_handler
    def get_product(self, product_id: int):
        return self.session.query(ProductEntity).filter(ProductEntity.id == product_id).first()

    @db_request_handler
    def last_product(self):
        return self.session.query(ProductEntity).order_by(ProductEntity.id.desc()).first()
