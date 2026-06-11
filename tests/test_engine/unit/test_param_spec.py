from __future__ import annotations

import pytest


def test_paramspec_defaults():
    from nest.engine.params import ParamSpec
    p = ParamSpec(source="query")
    assert p.source == "query"
    assert p.name is None
    assert p.annotation is None
    assert p.default is ...
    assert p.pipes == ()
    assert p.factory is None
    assert p.data is None


def test_paramspec_is_frozen():
    from nest.engine.params import ParamSpec
    p = ParamSpec(source="body", name="payload")
    with pytest.raises((AttributeError, TypeError)):
        p.name = "other"  # type: ignore[misc]


def test_paramspec_all_sources_valid():
    from nest.engine.params import ParamSpec, VALID_SOURCES
    for src in VALID_SOURCES:
        p = ParamSpec(source=src)
        assert p.source == src


def test_paramspec_with_pipes():
    from nest.engine.params import ParamSpec

    def trim(v):
        return v.strip()

    p = ParamSpec(source="query", name="q", pipes=(trim,))
    assert p.pipes == (trim,)


def test_paramspec_with_default():
    from nest.engine.params import ParamSpec
    p = ParamSpec(source="query", name="page", default=1)
    assert p.default == 1


def test_paramspec_with_custom_factory():
    from nest.engine.params import ParamSpec

    def my_factory(data, ctx):
        return "value"

    p = ParamSpec(source="custom", factory=my_factory, data={"key": "val"})
    assert p.factory is my_factory
    assert p.data == {"key": "val"}


def test_paramspec_invalid_source_raises():
    from nest.engine.params import ParamSpec
    with pytest.raises(ValueError, match="Invalid param source"):
        ParamSpec(source="invalid_source")
