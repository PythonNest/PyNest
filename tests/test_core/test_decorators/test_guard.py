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


def test_guard_added_to_route_dependencies():
    router = GuardController.get_router()
    route = router.routes[0]
    deps = route.dependencies
    assert len(deps) == 1
    assert callable(deps[0].dependency)


def _has_security_requirements(dependant):
    """Recursively check if a dependant or its dependencies have security requirements."""
    if dependant.security_requirements:
        return True
    
    for dep in dependant.dependencies:
        if _has_security_requirements(dep):
            return True
    
    return False


def test_openapi_security_requirement():
    @Controller("/bearer")
    class BearerController:
        @Get("/")
        @UseGuards(BearerGuard)
        def root(self):
            return {"ok": True}

    router = BearerController.get_router()
    route = router.routes[0]
    
    # Check if security requirements exist anywhere in the dependency tree
    assert _has_security_requirements(route.dependant), \
        "Security requirements should be present in the dependency tree for OpenAPI integration"
