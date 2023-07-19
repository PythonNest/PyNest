from typing import Union

from beanie import Document


class Product(Document):
    name: str
    price: float
    description: Union[str, None] = None
