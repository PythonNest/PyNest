from typing import List, Type
from examples.nest_products_mongo.src import BaseController
from examples.nest_products_mongo.src import BaseProvider


class BaseModule:
    def __init__(
        self,
        providers: List[Type[BaseProvider]] = None,
        controllers: List[Type[BaseController]] = None,
    ):
        providers: List[Type[BaseProvider]] = providers
        controllers: List[Type[BaseController]] = controllers
