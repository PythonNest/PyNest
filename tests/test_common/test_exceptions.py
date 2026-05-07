import pytest
from nest.common.exceptions import (
    HttpException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    MethodNotAllowedException,
    ConflictException,
    UnprocessableEntityException,
    InternalServerErrorException,
)


def test_http_exception_attributes():
    exc = HttpException(message="oops", status_code=418)
    assert exc.status_code == 418
    assert exc.message == "oops"
    assert str(exc) == "oops"


def test_http_exception_is_exception():
    exc = HttpException(message="x", status_code=400)
    assert isinstance(exc, Exception)


def test_bad_request_exception():
    exc = BadRequestException("bad input")
    assert exc.status_code == 400
    assert exc.message == "bad input"
    assert isinstance(exc, HttpException)


def test_unauthorized_exception():
    exc = UnauthorizedException("no auth")
    assert exc.status_code == 401
    assert isinstance(exc, HttpException)


def test_forbidden_exception():
    exc = ForbiddenException("forbidden")
    assert exc.status_code == 403
    assert isinstance(exc, HttpException)


def test_not_found_exception():
    exc = NotFoundException("not found")
    assert exc.status_code == 404
    assert isinstance(exc, HttpException)


def test_method_not_allowed_exception():
    exc = MethodNotAllowedException("method not allowed")
    assert exc.status_code == 405
    assert isinstance(exc, HttpException)


def test_conflict_exception():
    exc = ConflictException("conflict")
    assert exc.status_code == 409
    assert isinstance(exc, HttpException)


def test_unprocessable_entity_exception():
    exc = UnprocessableEntityException("unprocessable")
    assert exc.status_code == 422
    assert isinstance(exc, HttpException)


def test_internal_server_error_exception():
    exc = InternalServerErrorException("server error")
    assert exc.status_code == 500
    assert isinstance(exc, HttpException)


def test_default_message():
    exc = NotFoundException()
    assert exc.message == "Not Found"
    assert exc.status_code == 404


# --- ArgumentsHost / ExceptionFilter tests ---

from fastapi import Request
from fastapi.responses import JSONResponse

from nest.common.exceptions import (
    ArgumentsHost,
    HttpArgumentsHost,
    ExceptionFilter,
)


def test_arguments_host_switch_to_http():
    scope = {"type": "http", "method": "GET", "path": "/", "query_string": b"",
             "headers": [], "http_version": "1.1"}
    request = Request(scope=scope)
    host = ArgumentsHost(request=request)
    http_host = host.switch_to_http()
    assert isinstance(http_host, HttpArgumentsHost)


def test_http_arguments_host_get_request():
    scope = {"type": "http", "method": "GET", "path": "/", "query_string": b"",
             "headers": [], "http_version": "1.1"}
    request = Request(scope=scope)
    host = ArgumentsHost(request=request)
    assert host.switch_to_http().get_request() is request


def test_arguments_host_get_type():
    host = ArgumentsHost(request=None)
    assert host.get_type() == "http"


def test_exception_filter_is_abstract():
    with pytest.raises(TypeError):
        ExceptionFilter()


def test_exception_filter_subclass_must_implement_catch():
    class BadFilter(ExceptionFilter):
        pass

    with pytest.raises(TypeError):
        BadFilter()


def test_exception_filter_concrete_subclass():
    class GoodFilter(ExceptionFilter):
        async def catch(self, exception, host):
            return JSONResponse(status_code=400, content={"error": str(exception)})

    f = GoodFilter()
    assert f is not None
