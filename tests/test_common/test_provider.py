import pytest
from nest.common.provider import (
    InjectionToken,
    Scope,
    ProviderDescriptor,
    normalize_provider,
)


class SomeService:
    pass


class OtherService:
    pass


# --- InjectionToken ---

def test_injection_token_has_name():
    token = InjectionToken("DB_URL")
    assert token.name == "DB_URL"


def test_injection_token_repr():
    token = InjectionToken("MY_TOKEN")
    assert "MY_TOKEN" in repr(token)


def test_injection_tokens_with_same_name_are_equal():
    assert InjectionToken("A") == InjectionToken("A")


def test_injection_tokens_with_different_names_are_not_equal():
    assert InjectionToken("A") != InjectionToken("B")


def test_injection_token_is_hashable():
    token = InjectionToken("X")
    d = {token: "value"}
    assert d[token] == "value"


# --- Scope ---

def test_scope_values_exist():
    assert Scope.SINGLETON
    assert Scope.TRANSIENT
    assert Scope.REQUEST


# --- normalize_provider: class form ---

def test_normalize_class_provider_sets_use_class():
    desc = normalize_provider(SomeService)
    assert desc.provide is SomeService
    assert desc.use_class is SomeService
    assert desc.scope == Scope.SINGLETON


# --- normalize_provider: useValue dict ---

def test_normalize_use_value():
    desc = normalize_provider({"provide": "DB_URL", "useValue": "postgres://localhost/db"})
    assert desc.provide == "DB_URL"
    assert desc.use_value == "postgres://localhost/db"
    assert desc.use_class is None


# --- normalize_provider: useClass dict ---

def test_normalize_use_class():
    desc = normalize_provider({"provide": SomeService, "useClass": OtherService})
    assert desc.provide is SomeService
    assert desc.use_class is OtherService


# --- normalize_provider: useFactory dict ---

def test_normalize_use_factory():
    factory = lambda: SomeService()
    desc = normalize_provider({
        "provide": SomeService,
        "useFactory": factory,
        "inject": [OtherService],
    })
    assert desc.provide is SomeService
    assert desc.use_factory is factory
    assert desc.inject == [OtherService]


# --- normalize_provider: useExisting dict ---

def test_normalize_use_existing():
    desc = normalize_provider({"provide": SomeService, "useExisting": OtherService})
    assert desc.provide is SomeService
    assert desc.use_existing is OtherService


# --- normalize_provider: scope override ---

def test_normalize_scope_override():
    desc = normalize_provider({"provide": SomeService, "useClass": SomeService, "scope": Scope.TRANSIENT})
    assert desc.scope == Scope.TRANSIENT


# --- normalize_provider: invalid dict ---

def test_normalize_invalid_dict_raises():
    with pytest.raises(ValueError, match="Invalid provider descriptor"):
        normalize_provider({"provide": SomeService})


# --- normalize_provider: already a ProviderDescriptor ---

def test_normalize_passthrough_descriptor():
    desc = ProviderDescriptor(provide=SomeService, use_class=SomeService)
    result = normalize_provider(desc)
    assert result is desc
