import pytest
from injector import Injector
from nest.core.decorators.injectable import Injectable
from nest.common.provider import Scope


def test_injectable_marks_class():
    @Injectable
    class MyService:
        pass

    assert hasattr(MyService, "__injectable__")
    assert MyService.__injectable__ is True


def test_injectable_does_not_mutate_class_with_dep_attributes():
    @Injectable
    class Dep:
        pass

    @Injectable
    class MyService:
        def __init__(self, dep: Dep):
            self.dep = dep

    # The class must NOT have 'dep' as a class-level attribute
    assert "dep" not in MyService.__dict__


def test_injectable_preserves_init():
    @Injectable
    class MyService:
        def __init__(self, x: int = 5):
            self.x = x

    svc = MyService()
    assert svc.x == 5


def test_injectable_default_scope_is_singleton():
    @Injectable
    class MyService:
        pass

    assert MyService.__injectable_scope__ == Scope.SINGLETON


def test_injectable_with_transient_scope():
    @Injectable(scope=Scope.TRANSIENT)
    class MyService:
        pass

    assert MyService.__injectable_scope__ == Scope.TRANSIENT


def test_injectable_with_request_scope():
    @Injectable(scope=Scope.REQUEST)
    class MyService:
        pass

    assert MyService.__injectable_scope__ == Scope.REQUEST


def test_injector_resolves_injectable_class():
    @Injectable
    class Repo:
        def items(self):
            return [1, 2, 3]

    @Injectable
    class Service:
        def __init__(self, repo: Repo):
            self.repo = repo

    injector = Injector()
    svc = injector.get(Service)
    assert isinstance(svc, Service)
    assert isinstance(svc.repo, Repo)
    # dep must be on the INSTANCE, not on the class
    assert "repo" in svc.__dict__
    assert "repo" not in Service.__dict__
