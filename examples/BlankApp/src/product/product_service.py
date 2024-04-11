from nest.core.decorators import Injectable

from .product_model import Product


@Injectable
class ProductService:
    def __init__(self):
        self.database = []

    def get_product(self):
        return self.database

    def add_product(self, product: Product):
        self.database.append(product)
        return product
