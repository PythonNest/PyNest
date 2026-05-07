import inspect

from fastapi import Request

from fastapi.security import HTTPBearer

from nest.core import Controller, Get, UseGuards, BaseGuard


class SimpleGuard(BaseGuard):
    def __init__(self):
        self.called = False

    def can_activate(self, request: Request) -> bool:
        self.called = True
        return True


class BearerGuard(BaseGuard):
    security_scheme = HTTPBearer()

    def can_activate(self, request: Request, credentials) -> bool:
        return True


class JWTGuard(BaseGuard):
    security_scheme = HTTPBearer()

    def can_activate(self, request: Request, credentials=None) -> bool:
        if credentials and credentials.scheme == "Bearer":
            return self.validate_jwt(credentials.credentials)
        return False


@Controller("/guard")
class GuardController:
    @Get("/")
    @UseGuards(SimpleGuard)
    def root(self):
        return {"ok": True}


def test_use_guards_sets_attribute():
    assert hasattr(GuardController.root, "__guards__")
    assert SimpleGuard in GuardController.root.__guards__


def test_guard_metadata_stored_on_method():
    """Guards are stored as metadata on route methods for later route registration."""
    @Controller("/items")
    class ItemController:
        @Get("/")
        @UseGuards(SimpleGuard)
        def list_items(self):
            return []

    assert hasattr(ItemController.list_items, "__guards__")
    assert SimpleGuard in ItemController.list_items.__guards__


def test_guard_as_dependency_callable():
    """as_dependency() must produce a valid FastAPI Depends object."""
    dep = SimpleGuard.as_dependency()
    # FastAPI Depends wraps a callable in a Depends object
    assert callable(dep.dependency)


def test_bearer_guard_has_security_scheme():
    """Guards with security_scheme are recognized as having OpenAPI security."""
    assert BearerGuard.security_scheme is not None
    dep = BearerGuard.as_dependency()
    assert callable(dep.dependency)


def test_controller_preserves_guard_metadata():
    """@Controller must not strip guard metadata from route methods."""
    @Controller("/bearer")
    class BearerController:
        @Get("/")
        @UseGuards(BearerGuard)
        def root(self):
            return {"ok": True}

    assert hasattr(BearerController.root, "__guards__")
    assert BearerGuard in BearerController.root.__guards__
