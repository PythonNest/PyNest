import pytest
from injector import Injector
from nest.core.injector_module import build_injector
from nest.common.provider import ProviderDescriptor, Scope, InjectionToken
from nest.core.decorators.injectable import Injectable


@Injectable
class Repo:
    def find_all(self):
        return ["item1"]


@Injectable
class Service:
    def __init__(self, repo: Repo):
        self.repo = repo

    def get_items(self):
        return self.repo.find_all()


def test_build_injector_resolves_class_provider():
    descriptors = [
        ProviderDescriptor(provide=Repo, use_class=Repo),
        ProviderDescriptor(provide=Service, use_class=Service),
    ]
    injector = build_injector(descriptors)
    service = injector.get(Service)
    assert isinstance(service, Service)
    assert isinstance(service.repo, Repo)


def test_build_injector_singleton_scope_returns_same_instance():
    descriptors = [ProviderDescriptor(provide=Repo, use_class=Repo, scope=Scope.SINGLETON)]
    injector = build_injector(descriptors)
    a = injector.get(Repo)
    b = injector.get(Repo)
    assert a is b


def test_build_injector_transient_scope_returns_new_instance():
    descriptors = [ProviderDescriptor(provide=Repo, use_class=Repo, scope=Scope.TRANSIENT)]
    injector = build_injector(descriptors)
    a = injector.get(Repo)
    b = injector.get(Repo)
    assert a is not b


def test_build_injector_use_value_injection_token():
    token = InjectionToken("DB_URL")
    descriptors = [ProviderDescriptor(provide=token, use_value="postgres://localhost/test")]
    injector = build_injector(descriptors)
    value = injector.get(token)
    assert value == "postgres://localhost/test"


def test_build_injector_use_value_string_key():
    descriptors = [ProviderDescriptor(provide="DB_URL", use_value="postgres://localhost/test")]
    injector = build_injector(descriptors)
    value = injector.get("DB_URL")
    assert value == "postgres://localhost/test"


def test_build_injector_use_factory_no_deps():
    call_count = [0]

    def factory():
        call_count[0] += 1
        return Repo()

    descriptors = [ProviderDescriptor(provide=Repo, use_factory=factory, inject=[])]
    injector = build_injector(descriptors)
    result = injector.get(Repo)
    assert isinstance(result, Repo)
    assert call_count[0] == 1


def test_build_injector_use_factory_with_deps():
    descriptors = [
        ProviderDescriptor(provide=Repo, use_class=Repo),
        ProviderDescriptor(
            provide=Service,
            use_factory=lambda repo: Service(repo),
            inject=[Repo],
        ),
    ]
    injector = build_injector(descriptors)
    service = injector.get(Service)
    assert isinstance(service.repo, Repo)


def test_build_injector_use_existing_aliases():
    descriptors = [
        ProviderDescriptor(provide=Repo, use_class=Repo),
        ProviderDescriptor(provide=Service, use_class=Service),
        ProviderDescriptor(provide="IService", use_existing=Service),
    ]
    injector = build_injector(descriptors)
    service1 = injector.get(Service)
    service2 = injector.get("IService")
    assert service1 is service2


def test_use_class_different_from_provide():
    class MockRepo(Repo):
        def find_all(self):
            return []

    descriptors = [
        ProviderDescriptor(provide=Repo, use_class=MockRepo),
        ProviderDescriptor(provide=Service, use_class=Service),
    ]
    injector = build_injector(descriptors)
    service = injector.get(Service)
    assert isinstance(service.repo, MockRepo)
    assert service.get_items() == []
