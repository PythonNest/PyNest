import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from nest.core import Module, Injectable, Controller, Get, PyNestFactory
from nest.core.pynest_application import PyNestApp


@Injectable
class MessageService:
    def get_message(self) -> str:
        return "Hello, World!"


@Controller("/test", tag="test")
class TestController:
    def __init__(self, svc: MessageService):
        self.svc = svc

    @Get("/")
    def index(self):
        return {"message": self.svc.get_message()}


@Module(controllers=[TestController], providers=[MessageService])
class TestModule:
    pass


def test_create_returns_pynest_app():
    app = PyNestFactory.create(TestModule)
    assert isinstance(app, PyNestApp)


def test_create_produces_fastapi_server():
    app = PyNestFactory.create(TestModule)
    assert isinstance(app.get_server(), FastAPI)


def test_create_server_kwargs_forwarded():
    app = PyNestFactory.create(
        TestModule,
        title="Test Server",
        description="A test",
        version="1.0.0",
    )
    server = app.get_server()
    assert server.title == "Test Server"
    assert server.version == "1.0.0"


def test_e2e_route_responds():
    app = PyNestFactory.create(TestModule)
    client = TestClient(app.get_server())
    response = client.get("/test/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_two_apps_are_independent():
    app1 = PyNestFactory.create(TestModule)
    app2 = PyNestFactory.create(TestModule)
    svc1 = app1.container.get(MessageService)
    svc2 = app2.container.get(MessageService)
    assert svc1 is not svc2


def test_service_dep_is_instance_attribute_not_class():
    app = PyNestFactory.create(TestModule)
    ctrl = app.container.get_controller_instance(TestController)
    assert "svc" in ctrl.__dict__
    assert "svc" not in TestController.__dict__
