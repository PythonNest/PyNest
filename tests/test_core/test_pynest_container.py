import pytest
from nest.core.pynest_container import PyNestContainer
from nest.core.decorators.module import Module
from nest.core.decorators.injectable import Injectable


@Injectable
class RepoService:
    def find(self):
        return ["a", "b"]


@Injectable
class AppService:
    def __init__(self, repo: RepoService):
        self.repo = repo

    def items(self):
        return self.repo.find()


@Module(providers=[RepoService, AppService])
class AppModule:
    pass


@Module(providers=[RepoService], exports=[RepoService])
class RepoModule:
    pass


@Module(providers=[AppService], imports=[RepoModule])
class ServiceModule:
    pass


# ── Container is NOT a singleton ──────────────────────────────────────────────

def test_two_containers_are_independent():
    c1 = PyNestContainer()
    c2 = PyNestContainer()
    assert c1 is not c2


# ── add_module + build + get ──────────────────────────────────────────────────

def test_get_provider_after_build():
    container = PyNestContainer()
    container.add_module(AppModule)
    container.build()
    svc = container.get(AppService)
    assert isinstance(svc, AppService)


def test_get_returns_singleton_by_default():
    container = PyNestContainer()
    container.add_module(AppModule)
    container.build()
    a = container.get(AppService)
    b = container.get(AppService)
    assert a is b


def test_dependency_is_injected_into_instance():
    container = PyNestContainer()
    container.add_module(AppModule)
    container.build()
    svc = container.get(AppService)
    # Must be an instance attribute, NOT a class attribute
    assert "repo" in svc.__dict__
    assert isinstance(svc.repo, RepoService)


def test_provider_not_class_attribute_after_build():
    container = PyNestContainer()
    container.add_module(AppModule)
    container.build()
    # The class itself must not be mutated — dep is on the instance only
    assert "repo" not in AppService.__dict__


def test_add_module_inserts_true_for_new_module():
    container = PyNestContainer()
    result = container.add_module(AppModule)
    assert result["inserted"] is True


def test_add_module_inserts_false_for_duplicate():
    container = PyNestContainer()
    container.add_module(AppModule)
    result = container.add_module(AppModule)
    assert result["inserted"] is False


def test_imported_module_providers_are_resolvable():
    container = PyNestContainer()
    container.add_module(ServiceModule)
    container.build()
    svc = container.get(AppService)
    assert isinstance(svc.repo, RepoService)


# ── Cycle detection ───────────────────────────────────────────────────────────

def test_circular_dependency_raises_on_build():
    from nest.common.exceptions import CircularDependencyException

    @Injectable
    class Alpha:
        def __init__(self, b: "Beta"):
            self.b = b

    @Injectable
    class Beta:
        def __init__(self, a: Alpha):
            self.a = a

    @Module(providers=[Alpha, Beta])
    class CycleModule:
        pass

    container = PyNestContainer()
    container.add_module(CycleModule)
    with pytest.raises(CircularDependencyException):
        container.build()


# ── useValue provider ─────────────────────────────────────────────────────────

def test_use_value_provider():
    from nest.common.provider import InjectionToken

    DB_URL = InjectionToken("DB_URL")

    @Module(providers=[{"provide": DB_URL, "useValue": "postgres://localhost/test"}])
    class ValueModule:
        pass

    container = PyNestContainer()
    container.add_module(ValueModule)
    container.build()
    value = container.get(DB_URL)
    assert value == "postgres://localhost/test"


# ── get before build raises ───────────────────────────────────────────────────

def test_get_before_build_raises():
    container = PyNestContainer()
    container.add_module(AppModule)
    with pytest.raises(RuntimeError, match="build()"):
        container.get(AppService)
