# tests/test_engine/unit/test_types.py
from __future__ import annotations

import typing


def test_http_method_values():
    from nest.engine.types import HttpMethod
    assert HttpMethod.GET.value == "GET"
    assert HttpMethod.POST.value == "POST"
    assert HttpMethod.DELETE.value == "DELETE"
    assert HttpMethod.PUT.value == "PUT"
    assert HttpMethod.PATCH.value == "PATCH"
    assert HttpMethod.HEAD.value == "HEAD"
    assert HttpMethod.OPTIONS.value == "OPTIONS"


def test_endpoint_is_callable_alias():
    from nest.engine.types import Endpoint
    # Verify Endpoint is the correct generic alias, not just non-None
    assert Endpoint == typing.Callable[..., typing.Any]


def test_http_method_is_same_object_as_original():
    from nest.engine.types import HttpMethod
    from nest.core.decorators.http_method import HTTPMethod
    # Re-export must be identity — no copy or subclass
    assert HttpMethod is HTTPMethod


def test_engine_package_exports():
    import nest.engine as engine
    assert hasattr(engine, "AbstractHttpAdapter")
    assert hasattr(engine, "RouteSpec")
    assert hasattr(engine, "ParamSpec")
    assert hasattr(engine, "HttpMethod")
    assert hasattr(engine, "Endpoint")
    assert hasattr(engine, "ExecutionContext")
    assert hasattr(engine, "HttpExecutionContext")
    assert hasattr(engine, "VALID_SOURCES")
