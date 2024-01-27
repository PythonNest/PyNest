import pytest

from nest.core.decorators.controller import Controller, Get, Post, Delete, Put, Patch, Any


@Controller(tag="test", prefix="/api/v1")
class TestController:
    @Get("/get")
    def get_endpoint(self):
        return {"message": "GET endpoint"}

    @Post("/post")
    def post_endpoint(self):
        return {"message": "POST endpoint"}

    @Delete("/delete")
    def delete_endpoint(self):
        return {"message": "DELETE endpoint"}

    @Put("/put")
    def put_endpoint(self):
        return {"message": "PUT endpoint"}

    @Patch("/patch")
    def patch_endpoint(self):
        return {"message": "PATCH endpoint"}
    
    @Any("/any")
    def any_endpoint(self):
        return {"message": "Any endpoint"}

@pytest.fixture
def test_controller():
    return TestController()


@pytest.mark.parametrize(
    "function, endpoint, expected_message",
    [
        ("get_endpoint", "/get", "GET endpoint"),
        ("post_endpoint", "/post", "POST endpoint"),
        ("delete_endpoint", "/delete", "DELETE endpoint"),
        ("put_endpoint", "/put", "PUT endpoint"),
        ("patch_endpoint", "/patch", "PATCH endpoint"),
    ],
)
def test_endpoints(test_controller, function, endpoint, expected_message):
    attribute = getattr(test_controller, function)
    assert attribute.__path__ == "/api/v1" + endpoint
    assert attribute.__kwargs__ == {}
    assert attribute.method == function.split("_")[0].upper()
    assert attribute() == {"message": f"{function.split('_')[0].upper()} endpoint"}
