import inspect

from fastapi import Request

from nest.core import Controller, Get, UseGuards, BaseGuard


class SimpleGuard(BaseGuard):
    def __init__(self):
        self.called = False

    def can_activate(self, request: Request) -> bool:
        self.called = True
        return True


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
    assert isinstance(deps[0].dependency, SimpleGuard)
