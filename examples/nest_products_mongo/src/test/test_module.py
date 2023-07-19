from examples.nest_products_mongo.src.test.test_service import TestService
from examples.nest_products_mongo.src.test.test_controller import TestController


class TestModule:
    def __init__(self):
        self.providers = [TestService]
        self.controllers = [TestController]
