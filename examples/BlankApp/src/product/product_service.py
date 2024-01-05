from .product_model import Product
from functools import lru_cache
from nest.core.decorators import Injectable


@lru_cache()
@Injectable
class ProductService:

    def __init__(self):
        self.database = []
        
    def get_product(self):
        return self.database
    
    def add_product(self, product: Product):
        self.database.append(product)
        return product
        
