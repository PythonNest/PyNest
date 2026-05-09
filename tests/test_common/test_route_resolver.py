import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from nest.common.route_resolver import RoutesResolver
from nest.core.pynest_container import PyNestContainer
from nest.core.decorators.module import Module
from nest.core.decorators.injectable import Injectable
from nest.core.decorators.controller import Controller
from nest.core.decorators.http_method import Get, Post


@Injectable
class GreetService:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"


@Controller("/greet", tag="greet")
class GreetController:
    def __init__(self, svc: GreetService):
        self.svc = svc

    @Get("/")
    def index(self):
        return {"message": "ok"}

    @Get("/{name}")
    def greet(self, name: str):
        return {"message": self.svc.greet(name)}


@Module(providers=[GreetService], controllers=[GreetController])
class GreetModule:
    pass


@pytest.fixture
def app_and_container():
    container = PyNestContainer()
    container.add_module(GreetModule)
    container.build()
    app = FastAPI()
    resolver = RoutesResolver(container, app)
    resolver.register_routes()
    return app, container


def test_routes_registered(app_and_container):
    app, _ = app_and_container
    paths = {route.path for route in app.routes}
    assert any("/greet" in p for p in paths)


def test_get_index_returns_200(app_and_container):
    app, _ = app_and_container
    client = TestClient(app)
    response = client.get("/greet/")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}


def test_get_with_path_param(app_and_container):
    app, _ = app_and_container
    client = TestClient(app)
    response = client.get("/greet/World")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello, World!"


def test_service_is_instance_attribute_not_class(app_and_container):
    app, container = app_and_container
    instance = container.get_controller_instance(GreetController)
    assert "svc" in instance.__dict__
    assert "svc" not in GreetController.__dict__


def test_controller_instance_is_singleton(app_and_container):
    app, container = app_and_container
    a = container.get_controller_instance(GreetController)
    b = container.get_controller_instance(GreetController)
    assert a is b
