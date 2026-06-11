from __future__ import annotations
import pytest


def _make_endpoint():
    async def endpoint():
        return {"ok": True}
    return endpoint


def test_routespec_minimal():
    from nest.engine.route_spec import RouteSpec
    from nest.engine.types import HttpMethod
    ep = _make_endpoint()
    spec = RouteSpec(method=HttpMethod.GET, path="/", endpoint=ep)
    assert spec.method == HttpMethod.GET
    assert spec.path == "/"
    assert spec.endpoint is ep
    assert spec.params == ()
    assert spec.guards == ()
    assert spec.filters == ()
    assert spec.status_code is None
    assert spec.tags == ()
    assert spec.name is None
    assert spec.summary is None
    assert spec.description is None
    assert spec.extra == {}


def test_routespec_is_frozen():
    from nest.engine.route_spec import RouteSpec
    from nest.engine.types import HttpMethod
    ep = _make_endpoint()
    spec = RouteSpec(method=HttpMethod.POST, path="/items", endpoint=ep)
    with pytest.raises((AttributeError, TypeError)):
        spec.path = "/other"  # type: ignore[misc]


def test_routespec_with_params():
    from nest.engine.route_spec import RouteSpec
    from nest.engine.params import ParamSpec
    from nest.engine.types import HttpMethod
    ep = _make_endpoint()
    p = ParamSpec(source="query", name="page", default=1)
    spec = RouteSpec(method=HttpMethod.GET, path="/items", endpoint=ep, params=(p,))
    assert spec.params == (p,)


def test_routespec_extra_is_independent_per_instance():
    from nest.engine.route_spec import RouteSpec
    from nest.engine.types import HttpMethod
    ep = _make_endpoint()
    spec1 = RouteSpec(method=HttpMethod.GET, path="/a", endpoint=ep)
    spec2 = RouteSpec(method=HttpMethod.GET, path="/b", endpoint=ep)
    assert spec1.extra is not spec2.extra


def test_routespec_full():
    from nest.engine.route_spec import RouteSpec
    from nest.engine.params import ParamSpec
    from nest.engine.types import HttpMethod
    ep = _make_endpoint()
    p = ParamSpec(source="body", name="data")
    spec = RouteSpec(
        method=HttpMethod.POST,
        path="/users",
        endpoint=ep,
        params=(p,),
        status_code=201,
        tags=("users",),
        name="create_user",
        summary="Create a user",
        description="Creates a new user record.",
        extra={"response_model_exclude_none": True},
    )
    assert spec.status_code == 201
    assert spec.tags == ("users",)
    assert spec.name == "create_user"
    assert spec.extra == {"response_model_exclude_none": True}
