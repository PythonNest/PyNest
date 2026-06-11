import pytest
from unittest.mock import MagicMock

from nest.core import Controller, Get, Injectable, Module
from nest.testing import PyNestTestingModule


@Injectable
class UserRepository:
    def find_all(self):
        return ["alice", "bob"]


@Injectable
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def list_users(self):
        return self.repo.find_all()


@Controller("/users")
class UserController:
    def __init__(self, service: UserService):
        self.service = service

    @Get("/")
    def list_users(self):
        return {"users": self.service.list_users()}


@Module(controllers=[UserController], providers=[UserService, UserRepository])
class UserModule:
    pass


class FakeUserRepository:
    def find_all(self):
        return ["fake"]


# ── compile & get ──────────────────────────────────────────────────────────────


def test_compile_resolves_wired_provider():
    module = PyNestTestingModule.create_testing_module(
        providers=[UserService, UserRepository]
    ).compile()
    service = module.get(UserService)
    assert isinstance(service, UserService)
    assert service.list_users() == ["alice", "bob"]


@pytest.mark.asyncio
async def test_compile_is_awaitable():
    module = await PyNestTestingModule.create_testing_module(
        providers=[UserService, UserRepository]
    ).compile()
    assert isinstance(module.get(UserService), UserService)


def test_compile_from_imports_resolves_module_graph():
    module = PyNestTestingModule.create_testing_module(imports=[UserModule]).compile()
    assert module.get(UserService).list_users() == ["alice", "bob"]


def test_get_controller_instance():
    module = PyNestTestingModule.create_testing_module(imports=[UserModule]).compile()
    controller = module.get(UserController)
    assert isinstance(controller, UserController)
    assert controller.list_users() == {"users": ["alice", "bob"]}


def test_singleton_providers_return_same_instance():
    module = PyNestTestingModule.create_testing_module(imports=[UserModule]).compile()
    assert module.get(UserService) is module.get(UserService)


def test_two_testing_modules_are_isolated():
    first = PyNestTestingModule.create_testing_module(imports=[UserModule]).compile()
    second = PyNestTestingModule.create_testing_module(imports=[UserModule]).compile()
    assert first.get(UserService) is not second.get(UserService)


# ── provider overrides ─────────────────────────────────────────────────────────


def test_override_provider_use_value():
    module = (
        PyNestTestingModule.create_testing_module(imports=[UserModule])
        .override_provider(UserRepository)
        .use_value(FakeUserRepository())
        .compile()
    )
    assert module.get(UserService).list_users() == ["fake"]


def test_override_provider_use_class():
    module = (
        PyNestTestingModule.create_testing_module(imports=[UserModule])
        .override_provider(UserRepository)
        .use_class(FakeUserRepository)
        .compile()
    )
    assert module.get(UserService).list_users() == ["fake"]


def test_override_provider_use_factory():
    module = (
        PyNestTestingModule.create_testing_module(imports=[UserModule])
        .override_provider(UserRepository)
        .use_factory(lambda: FakeUserRepository())
        .compile()
    )
    assert module.get(UserService).list_users() == ["fake"]


def test_override_unknown_provider_raises():
    class NotRegistered:
        pass

    builder = (
        PyNestTestingModule.create_testing_module(imports=[UserModule])
        .override_provider(NotRegistered)
        .use_value(MagicMock())
    )
    with pytest.raises(ValueError, match="NotRegistered"):
        builder.compile()


# ── auto-mock ──────────────────────────────────────────────────────────────────


def test_use_auto_mock_replaces_providers_with_mocks():
    module = (
        PyNestTestingModule.create_testing_module(imports=[UserModule])
        .use_auto_mock()
        .compile()
    )
    repo = module.get(UserRepository)
    repo.find_all.return_value = ["mocked"]
    assert repo.find_all() == ["mocked"]


def test_use_auto_mock_respects_exclude():
    module = (
        PyNestTestingModule.create_testing_module(imports=[UserModule])
        .use_auto_mock(exclude=[UserService])
        .compile()
    )
    service = module.get(UserService)
    assert isinstance(service, UserService)
    service.repo.find_all.return_value = ["mocked"]
    assert service.list_users() == ["mocked"]


def test_explicit_override_wins_over_auto_mock():
    module = (
        PyNestTestingModule.create_testing_module(imports=[UserModule])
        .use_auto_mock()
        .override_provider(UserRepository)
        .use_value(FakeUserRepository())
        .compile()
    )
    assert module.get(UserRepository).find_all() == ["fake"]


@pytest.mark.asyncio
async def test_auto_mock_creates_async_mocks_for_async_methods():
    @Injectable
    class AsyncRepository:
        async def find_all(self):
            return ["real"]

    @Module(providers=[AsyncRepository])
    class AsyncModule:
        pass

    module = (
        PyNestTestingModule.create_testing_module(imports=[AsyncModule])
        .use_auto_mock()
        .compile()
    )
    repo = module.get(AsyncRepository)
    repo.find_all.return_value = ["mocked"]
    assert await repo.find_all() == ["mocked"]


# ── lifecycle ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_init_and_close_run_lifecycle_hooks():
    events = []

    @Injectable
    class LifecycleService:
        def on_module_init(self):
            events.append("init")

        def on_module_destroy(self):
            events.append("destroy")

    @Module(providers=[LifecycleService])
    class LifecycleModule:
        pass

    module = PyNestTestingModule.create_testing_module(
        imports=[LifecycleModule]
    ).compile()
    assert events == []

    await module.init()
    assert events == ["init"]

    await module.close()
    assert events == ["init", "destroy"]


@pytest.mark.asyncio
async def test_async_context_manager_runs_init_and_close():
    events = []

    @Injectable
    class CtxService:
        def on_module_init(self):
            events.append("init")

        def on_module_destroy(self):
            events.append("destroy")

    @Module(providers=[CtxService])
    class CtxModule:
        pass

    async with PyNestTestingModule.create_testing_module(
        imports=[CtxModule]
    ).compile() as module:
        assert isinstance(module.get(CtxService), CtxService)
        assert events == ["init"]

    assert events == ["init", "destroy"]
