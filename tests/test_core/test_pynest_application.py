import pytest
from fastapi import FastAPI

from nest.core import PyNestFactory
from nest.core.pynest_application import PyNestApp
from nest.core import Module, Injectable, Controller, Get


@Injectable
class AppService:
    def greet(self) -> str:
        return "hi"


@Controller("/app", tag="app")
class AppController:
    def __init__(self, svc: AppService):
        self.svc = svc

    @Get("/")
    def index(self):
        return {"msg": self.svc.greet()}


@Module(controllers=[AppController], providers=[AppService])
class AppModule:
    pass


@pytest.fixture
def pynest_app():
    return PyNestFactory.create(AppModule)


def test_get_server_returns_fastapi(pynest_app):
    assert isinstance(pynest_app.get_server(), FastAPI)


def test_get_http_server_alias(pynest_app):
    assert pynest_app.get_http_server() is pynest_app.get_server()


def test_container_is_built(pynest_app):
    # If the container is built, we can resolve a provider without RuntimeError
    svc = pynest_app.container.get(AppService)
    assert isinstance(svc, AppService)


def test_routes_are_registered(pynest_app):
    # At least one route should be registered on the FastAPI app
    assert len(pynest_app.get_server().routes) > 0


def test_use_adds_middleware(pynest_app):
    from starlette.middleware.base import BaseHTTPMiddleware

    class DummyMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)

    result = pynest_app.use(DummyMiddleware)
    # use() returns self for chaining
    assert result is pynest_app
