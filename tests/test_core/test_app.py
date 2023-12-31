from nest.core import App, Controller, Put, Get, Post, Delete, Patch, Depends
import pytest
from fastapi.routing import APIRoute
from fastapi import FastAPI


@Controller("test")
class TestController:
    @Get("/get")
    def get(self):
        return {"message": "Hello, World!"}

    @Post("/post")
    def post(self):
        return {"message": "Hello, World!"}

    @Put("/put")
    def put(self):
        return {"message": "Hello, World!"}

    @Delete("/delete")
    def delete(self):
        return {"message": "Hello, World!"}

    @Patch("/patch")
    def patch(self):
        return {"message": "Hello, World!"}


class TestModule:
    def __init__(self):
        self.controllers = [TestController]


@pytest.fixture(scope="module")
def app():
    return App(description="Test App", modules=[TestModule])


@pytest.mark.parametrize("route", ["/get", "/post", "/put", "/delete", "/patch"])
def test_get(app, route):
    route = "/test" + route # if prefix is not defined in the controller, then the given tag will be used as prefix
    route_exist = False
    for app_route in app.routes:
        if isinstance(app_route, APIRoute):
            if route == app_route.path:
                route_exist = True
    assert route_exist


def test_app_description(app):
    assert app.description == "Test App"


def test_app_modules(app):
    assert app.modules == [TestModule]


def test_app_type(app):
    assert isinstance(app, FastAPI)
