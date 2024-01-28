from nest.core import Module, Controller, Get
from nest.core import PyNestContainer
import pytest


@Controller("test")
class TestController:

    @Get("/")
    def get_test(self):
        return {"message": "GET endpoint"}


@Module(controllers=[TestController])
class TestModule:
    pass


@pytest.fixture
def test_module():
    return TestModule


@pytest.fixture
def test_container():
    return PyNestContainer()
