import pytest
from fastapi import FastAPI

from nest.common.route_resolver import RoutesResolver
from nest.core import (
    Controller,
    Get,
    Injectable,
    Module,
    PyNestContainer,
    PyNestFactory,
)
from nest.core.pynest_application import PyNestApp


@Injectable
class TestService:
    def get_message(self):
        return "Hello, World!"


@Controller("test")
class TestController:
    def __init__(self, test_service: TestService):
        self.test_service = test_service

    @Get("/")
    def get_test(self):
        return {"message": "GET endpoint"}

    @Get("/message")
    def get_message(self):
        return {"message": self.test_service.get_message()}


@Module(controllers=[TestController], providers=[TestService], exports=[TestService])
class TestModule:
    pass


@pytest.fixture
def test_module():
    return TestModule


@pytest.fixture
def test_server() -> FastAPI:
    server = PyNestFactory._create_server(
        title="Test Server",
        description="This is a test server",
        version="1.0.0",
        debug=True,
    )
    return server


@pytest.fixture
def test_container():
    return PyNestContainer()


@pytest.fixture
def test_resolver(test_container, test_server):
    return RoutesResolver(test_container, test_server)
