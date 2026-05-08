"""Integration tests for exception filters using TestClient."""
import pytest
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from nest.common.exceptions import (
    ArgumentsHost,
    ExceptionFilter,
    HttpException,
    NotFoundException,
    BadRequestException,
    InternalServerErrorException,
)
from nest.core import (
    Controller,
    Get,
    Module,
    Injectable,
    PyNestFactory,
)
from nest.core.decorators.filters import Catch, UseFilters


# ---------------------------------------------------------------------------
# Shared filter definitions
# ---------------------------------------------------------------------------

@Catch(HttpException)
class HttpExceptionFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentsHost):
        return JSONResponse(
            status_code=exception.status_code,
            content={"statusCode": exception.status_code, "message": exception.message, "source": "HttpExceptionFilter"},
        )


@Catch(ValueError)
class ValueErrorFilter(ExceptionFilter):
    async def catch(self, exception: ValueError, host: ArgumentsHost):
        return JSONResponse(
            status_code=400,
            content={"statusCode": 400, "message": str(exception), "source": "ValueErrorFilter"},
        )


@Catch()
class AllExceptionsFilter(ExceptionFilter):
    async def catch(self, exception: Exception, host: ArgumentsHost):
        return JSONResponse(
            status_code=500,
            content={"statusCode": 500, "message": "all exceptions caught", "source": "AllExceptionsFilter"},
        )


# ---------------------------------------------------------------------------
# Test 1: Global filter catches HttpException
# ---------------------------------------------------------------------------

@Injectable
class NoopService1:
    pass


@Controller("/t1")
class T1Controller:
    def __init__(self, svc: NoopService1):
        self.svc = svc

    @Get("/not-found")
    def raise_not_found(self):
        raise NotFoundException("resource missing")

    @Get("/ok")
    def ok(self):
        return {"status": "ok"}


@Module(controllers=[T1Controller], providers=[NoopService1])
class T1Module:
    pass


def test_global_http_exception_filter():
    app = PyNestFactory.create(T1Module)
    app.use_global_filters(HttpExceptionFilter())
    client = TestClient(app.get_server(), raise_server_exceptions=False)

    resp = client.get("/t1/not-found")
    assert resp.status_code == 404
    body = resp.json()
    assert body["message"] == "resource missing"
    assert body["source"] == "HttpExceptionFilter"


def test_global_filter_does_not_affect_ok_routes():
    app = PyNestFactory.create(T1Module)
    app.use_global_filters(HttpExceptionFilter())
    client = TestClient(app.get_server(), raise_server_exceptions=False)

    resp = client.get("/t1/ok")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Test 2: Controller-level @UseFilters
# ---------------------------------------------------------------------------

@Injectable
class NoopService2:
    pass


@Controller("/t2")
@UseFilters(HttpExceptionFilter)
class T2Controller:
    def __init__(self, svc: NoopService2):
        self.svc = svc

    @Get("/not-found")
    def raise_not_found(self):
        raise NotFoundException("t2 not found")

    @Get("/ok")
    def ok(self):
        return {"status": "ok"}


@Module(controllers=[T2Controller], providers=[NoopService2])
class T2Module:
    pass


def test_controller_level_filter_catches_http_exception():
    app = PyNestFactory.create(T2Module)
    client = TestClient(app.get_server(), raise_server_exceptions=False)

    resp = client.get("/t2/not-found")
    assert resp.status_code == 404
    body = resp.json()
    assert body["source"] == "HttpExceptionFilter"


def test_controller_level_filter_ok_route_unaffected():
    app = PyNestFactory.create(T2Module)
    client = TestClient(app.get_server(), raise_server_exceptions=False)

    resp = client.get("/t2/ok")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Test 3: Route-level @UseFilters takes priority over controller-level
# ---------------------------------------------------------------------------

@Injectable
class NoopService3:
    pass


@Catch(NotFoundException)
class NotFoundFilter(ExceptionFilter):
    async def catch(self, exception, host):
        return JSONResponse(
            status_code=404,
            content={"statusCode": 404, "message": exception.message, "source": "NotFoundFilter"},
        )


@Controller("/t3")
@UseFilters(HttpExceptionFilter)  # controller-level: handles all HttpException
class T3Controller:
    def __init__(self, svc: NoopService3):
        self.svc = svc

    @Get("/not-found")
    @UseFilters(NotFoundFilter)  # route-level: more specific, takes priority
    def raise_not_found(self):
        raise NotFoundException("t3 not found")

    @Get("/bad-request")
    def raise_bad_request(self):
        raise BadRequestException("t3 bad request")


@Module(controllers=[T3Controller], providers=[NoopService3])
class T3Module:
    pass


def test_route_level_filter_takes_priority_over_controller():
    app = PyNestFactory.create(T3Module)
    client = TestClient(app.get_server(), raise_server_exceptions=False)

    resp = client.get("/t3/not-found")
    assert resp.status_code == 404
    assert resp.json()["source"] == "NotFoundFilter"


def test_controller_level_filter_handles_unmatched_by_route():
    app = PyNestFactory.create(T3Module)
    client = TestClient(app.get_server(), raise_server_exceptions=False)

    resp = client.get("/t3/bad-request")
    assert resp.status_code == 400
    assert resp.json()["source"] == "HttpExceptionFilter"


# ---------------------------------------------------------------------------
# Test 4: Catch-all global filter (@Catch())
# ---------------------------------------------------------------------------

@Injectable
class NoopService4:
    pass


@Controller("/t4")
class T4Controller:
    def __init__(self, svc: NoopService4):
        self.svc = svc

    @Get("/runtime-error")
    def raise_runtime(self):
        raise RuntimeError("unexpected failure")


@Module(controllers=[T4Controller], providers=[NoopService4])
class T4Module:
    pass


def test_global_catch_all_filter():
    app = PyNestFactory.create(T4Module)
    app.use_global_filters(AllExceptionsFilter())
    client = TestClient(app.get_server(), raise_server_exceptions=False)

    resp = client.get("/t4/runtime-error")
    assert resp.status_code == 500
    assert resp.json()["source"] == "AllExceptionsFilter"


# ---------------------------------------------------------------------------
# Test 5: Filter does not catch non-matching exception type
# ---------------------------------------------------------------------------

@Injectable
class NoopService5:
    pass


@Controller("/t5")
@UseFilters(ValueErrorFilter)  # only catches ValueError
class T5Controller:
    def __init__(self, svc: NoopService5):
        self.svc = svc

    @Get("/value-error")
    def raise_value_error(self):
        raise ValueError("bad value")

    @Get("/runtime-error")
    def raise_runtime_error(self):
        raise RuntimeError("unexpected")


@Module(controllers=[T5Controller], providers=[NoopService5])
class T5Module:
    pass


def test_filter_catches_matching_exception():
    app = PyNestFactory.create(T5Module)
    client = TestClient(app.get_server(), raise_server_exceptions=False)

    resp = client.get("/t5/value-error")
    assert resp.status_code == 400
    assert resp.json()["source"] == "ValueErrorFilter"


def test_filter_ignores_non_matching_exception():
    app = PyNestFactory.create(T5Module)
    client = TestClient(app.get_server(), raise_server_exceptions=False)

    # RuntimeError is not caught by ValueErrorFilter → propagates → 500
    resp = client.get("/t5/runtime-error")
    assert resp.status_code == 500


# ---------------------------------------------------------------------------
# Test 6: ArgumentsHost provides request access in filter
# ---------------------------------------------------------------------------

@Injectable
class NoopService6:
    pass


@Catch(NotFoundException)
class RequestAwareFilter(ExceptionFilter):
    async def catch(self, exception: NotFoundException, host: ArgumentsHost):
        http = host.switch_to_http()
        request = http.get_request()
        path = request.url.path if request else "unknown"
        return JSONResponse(
            status_code=404,
            content={"path": path, "message": exception.message},
        )


@Controller("/t6")
@UseFilters(RequestAwareFilter)
class T6Controller:
    def __init__(self, svc: NoopService6):
        self.svc = svc

    @Get("/item")
    def get_item(self):
        raise NotFoundException("item not found")


@Module(controllers=[T6Controller], providers=[NoopService6])
class T6Module:
    pass


def test_filter_receives_request_via_arguments_host():
    app = PyNestFactory.create(T6Module)
    client = TestClient(app.get_server(), raise_server_exceptions=False)

    resp = client.get("/t6/item")
    assert resp.status_code == 404
    body = resp.json()
    assert body["path"] == "/t6/item"
    assert body["message"] == "item not found"


# ---------------------------------------------------------------------------
# Test 7: Async filter works
# ---------------------------------------------------------------------------

@Injectable
class NoopService7:
    pass


@Catch(HttpException)
class AsyncHttpFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentsHost):
        import asyncio
        await asyncio.sleep(0)  # prove it's awaited
        return JSONResponse(
            status_code=exception.status_code,
            content={"message": exception.message, "source": "AsyncHttpFilter"},
        )


@Controller("/t7")
@UseFilters(AsyncHttpFilter)
class T7Controller:
    def __init__(self, svc: NoopService7):
        self.svc = svc

    @Get("/error")
    def raise_error(self):
        raise InternalServerErrorException("server boom")


@Module(controllers=[T7Controller], providers=[NoopService7])
class T7Module:
    pass


def test_async_filter_is_awaited():
    app = PyNestFactory.create(T7Module)
    client = TestClient(app.get_server(), raise_server_exceptions=False)

    resp = client.get("/t7/error")
    assert resp.status_code == 500
    assert resp.json()["source"] == "AsyncHttpFilter"
