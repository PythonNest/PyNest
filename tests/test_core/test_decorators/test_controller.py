import pytest

from nest.core import Controller, Delete, Get, Injectable, Patch, Post, Put


@Controller(prefix="api/v1/user", tag="test")
class TestController:
    def __init__(self): ...

    @Get("/get_all_users")
    def get_endpoint(self):
        return {"message": "GET endpoint"}

    @Post("/create_user")
    def post_endpoint(self):
        return {"message": "POST endpoint"}

    @Delete("/delete_user")
    def delete_endpoint(self):
        return {"message": "DELETE endpoint"}

    @Put("/update_user")
    def put_endpoint(self):
        return {"message": "PUT endpoint"}

    @Patch("/patch_user")
    def patch_endpoint(self):
        return {"message": "PATCH endpoint"}


@pytest.fixture
def test_controller():
    return TestController()


@pytest.mark.parametrize(
    "function, endpoint, expected_message",
    [
        ("get_endpoint", "get_all_users", "GET endpoint"),
        ("post_endpoint", "create_user", "POST endpoint"),
        ("delete_endpoint", "delete_user", "DELETE endpoint"),
        ("put_endpoint", "update_user", "PUT endpoint"),
        ("patch_endpoint", "patch_user", "PATCH endpoint"),
    ],
)
def test_endpoints(test_controller, function, endpoint, expected_message):
    attribute = getattr(test_controller, function)
    assert attribute.__route_path__ == "/api/v1/user/" + endpoint
    assert attribute.__kwargs__ == {}
    assert attribute.__http_method__.value == function.split("_")[0].upper()
    assert attribute() == {"message": f"{function.split('_')[0].upper()} endpoint"}
