from __future__ import annotations


def test_execution_context_http():
    from nest.engine.execution_context import ExecutionContext
    sentinel_req = object()
    sentinel_res = object()
    ctx = ExecutionContext(request=sentinel_req, response=sentinel_res)
    http = ctx.switch_to_http()
    assert http.get_request() is sentinel_req
    assert http.get_response() is sentinel_res


def test_execution_context_get_type():
    from nest.engine.execution_context import ExecutionContext
    ctx = ExecutionContext(request=object())
    assert ctx.get_type() == "http"


def test_execution_context_response_optional():
    from nest.engine.execution_context import ExecutionContext
    ctx = ExecutionContext(request=object())
    http = ctx.switch_to_http()
    assert http.get_response() is None


def test_http_execution_context_standalone():
    from nest.engine.execution_context import HttpExecutionContext
    req = object()
    http = HttpExecutionContext(request=req)
    assert http.get_request() is req
    assert http.get_response() is None


def test_execution_context_holds_raw_objects():
    from nest.engine.execution_context import ExecutionContext
    # Verify it accepts any object — not just fastapi.Request
    class FakeRequest:
        pass
    class FakeResponse:
        pass
    req, res = FakeRequest(), FakeResponse()
    ctx = ExecutionContext(request=req, response=res)
    http = ctx.switch_to_http()
    assert isinstance(http.get_request(), FakeRequest)
    assert isinstance(http.get_response(), FakeResponse)
