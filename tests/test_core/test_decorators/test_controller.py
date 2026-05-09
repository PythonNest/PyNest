import pytest
from nest.core.decorators.controller import Controller
from nest.core.decorators.injectable import Injectable
from nest.core.decorators.http_method import Get, Post


@Injectable
class TestService:
    def hello(self):
        return "hello"


def test_controller_marks_class():
    @Controller("/items")
    class ItemController:
        def __init__(self, svc: TestService):
            self.svc = svc

    assert ItemController.__is_controller__ is True


def test_controller_stores_prefix():
    @Controller("/items")
    class ItemController:
        pass

    assert ItemController.__route_prefix__ == "/items"


def test_controller_stores_tag():
    @Controller("/items", tag="items")
    class ItemController:
        pass

    assert ItemController.__controller_tag__ == "items"


def test_controller_adds_leading_slash():
    @Controller("users")
    class UserController:
        pass

    assert UserController.__route_prefix__ == "/users"


def test_controller_strips_trailing_slash():
    @Controller("/users/")
    class UserController:
        pass

    assert UserController.__route_prefix__ == "/users"


def test_controller_does_not_delete_init():
    @Controller("/items")
    class ItemController:
        def __init__(self, svc: TestService):
            self.svc = svc

    # __init__ must still exist on the class — the injector needs it
    assert callable(getattr(ItemController, "__init__", None))


def test_controller_does_not_set_class_attributes_for_deps():
    @Controller("/items")
    class ItemController:
        def __init__(self, svc: TestService):
            self.svc = svc

    # Dep must NOT be a class attribute — injector handles instance creation
    assert "svc" not in ItemController.__dict__


def test_controller_returns_original_class():
    @Controller("/items")
    class ItemController:
        pass

    assert isinstance(ItemController, type)


def test_controller_http_methods_retain_metadata():
    @Controller("/items")
    class ItemController:
        @Get("/")
        def list_items(self):
            return []

        @Post("/")
        def create_item(self):
            return {}

    assert hasattr(ItemController.list_items, "__http_method__")
    assert hasattr(ItemController.create_item, "__http_method__")


def test_controller_with_no_prefix():
    @Controller()
    class RootController:
        pass

    assert RootController.__route_prefix__ is None
