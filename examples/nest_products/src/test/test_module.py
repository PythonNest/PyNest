from .test_service import TestService
from .test_controller import TestController


class TestModule:
    def __init__(self):
        self.providers = [TestService]
        self.controllers = [TestController]
