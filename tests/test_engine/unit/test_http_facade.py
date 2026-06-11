from __future__ import annotations


def test_request_is_fastapi_request():
    from nest.http import Request
    from fastapi import Request as FastAPIRequest
    assert Request is FastAPIRequest


def test_response_is_fastapi_response():
    from nest.http import Response
    from fastapi import Response as FastAPIResponse
    assert Response is FastAPIResponse


def test_depends_is_fastapi_depends():
    from nest.http import Depends
    from fastapi import Depends as FastAPIDepends
    assert Depends is FastAPIDepends


def test_http_exception_is_fastapi_http_exception():
    from nest.http import HTTPException
    from fastapi import HTTPException as FastAPIHTTPException
    assert HTTPException is FastAPIHTTPException


def test_all_exports_present():
    import nest.http as http
    for name in ["Request", "Response", "Depends", "HTTPException"]:
        assert hasattr(http, name), f"nest.http missing: {name}"
