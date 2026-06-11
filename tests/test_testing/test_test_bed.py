import pytest
from unittest.mock import AsyncMock, Mock

from nest.core import Injectable
from nest.testing import TestBed


@Injectable
class Database:
    def query(self, sql: str):
        raise RuntimeError("real database should never be hit in unit tests")


@Injectable
class CacheService:
    def get(self, key: str):
        return None

    def set(self, key: str, value):
        pass


@Injectable
class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    def find_all(self):
        return self.db.query("select * from users")


@Injectable
class UserService:
    def __init__(self, repo: UserRepository, cache: CacheService):
        self.repo = repo
        self.cache = cache

    def get_users(self):
        cached = self.cache.get("users")
        if cached is not None:
            return cached
        users = self.repo.find_all()
        self.cache.set("users", users)
        return users


@Injectable
class AsyncNotifier:
    async def send(self, message: str):
        raise RuntimeError("real notifier should never be hit")


@Injectable
class SignupService:
    def __init__(self, notifier: AsyncNotifier):
        self.notifier = notifier

    async def signup(self, email: str):
        await self.notifier.send(f"welcome {email}")
        return {"email": email}


# ── solitary ───────────────────────────────────────────────────────────────────


def test_solitary_unit_is_real_and_deps_are_mocked():
    unit, unit_ref = TestBed.solitary(UserService).compile()
    assert isinstance(unit, UserService)

    unit_ref.get(UserRepository).find_all.return_value = ["alice"]
    unit_ref.get(CacheService).get.return_value = None

    assert unit.get_users() == ["alice"]
    unit_ref.get(CacheService).set.assert_called_once_with("users", ["alice"])


def test_unit_ref_returns_the_injected_mock():
    unit, unit_ref = TestBed.solitary(UserService).compile()
    assert unit.repo is unit_ref.get(UserRepository)
    assert unit.cache is unit_ref.get(CacheService)


def test_compile_result_supports_attribute_access():
    result = TestBed.solitary(UserService).compile()
    assert isinstance(result.unit, UserService)
    assert result.unit_ref.get(UserRepository) is result.unit.repo


@pytest.mark.asyncio
async def test_async_dependency_methods_become_async_mocks():
    unit, unit_ref = TestBed.solitary(SignupService).compile()
    assert await unit.signup("a@b.com") == {"email": "a@b.com"}
    unit_ref.get(AsyncNotifier).send.assert_awaited_once_with("welcome a@b.com")


def test_mock_using_configures_the_mock():
    unit, unit_ref = (
        TestBed.solitary(UserService)
        .mock(UserRepository)
        .using(find_all=Mock(return_value=["bob"]))
        .mock(CacheService)
        .using(get=Mock(return_value=None))
        .compile()
    )
    assert unit.get_users() == ["bob"]


def test_mock_final_replaces_dependency_entirely():
    class InMemoryRepo:
        def find_all(self):
            return ["from-memory"]

    fake = InMemoryRepo()
    unit, unit_ref = (
        TestBed.solitary(UserService)
        .mock(UserRepository)
        .final(fake)
        .mock(CacheService)
        .using(get=Mock(return_value=None))
        .compile()
    )
    assert unit.repo is fake
    assert unit_ref.get(UserRepository) is fake
    assert unit.get_users() == ["from-memory"]


def test_unit_with_no_dependencies():
    unit, unit_ref = TestBed.solitary(Database).compile()
    assert isinstance(unit, Database)


def test_unit_ref_unknown_dependency_raises():
    _, unit_ref = TestBed.solitary(UserService).compile()
    with pytest.raises(KeyError, match="Database"):
        unit_ref.get(Database)


# ── sociable ───────────────────────────────────────────────────────────────────


def test_sociable_exposes_real_dependency():
    unit, unit_ref = (
        TestBed.sociable(UserService).expose(UserRepository).compile()
    )
    # UserRepository is real; its own Database dependency is mocked.
    assert isinstance(unit.repo, UserRepository)
    unit_ref.get(Database).query.return_value = ["from-db"]
    unit_ref.get(CacheService).get.return_value = None

    assert unit.get_users() == ["from-db"]
    unit_ref.get(Database).query.assert_called_once_with("select * from users")


def test_sociable_exposed_dependency_accessible_via_unit_ref():
    unit, unit_ref = (
        TestBed.sociable(UserService).expose(UserRepository).compile()
    )
    assert unit_ref.get(UserRepository) is unit.repo
