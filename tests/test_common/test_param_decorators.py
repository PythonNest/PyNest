from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from nest.common.decorators import (
    Body,
    ExecutionContext,
    Headers,
    HostParam,
    Ip,
    Param,
    Query,
    Req,
    Res,
    createParamDecorator,
)
from nest.common.route_resolver import RoutesResolver
from nest.core.decorators.controller import Controller
from nest.core.decorators.http_method import Get, Post
from nest.core.decorators.module import Module
from nest.core.pynest_container import PyNestContainer


def build_client(controller):
    @Module(controllers=[controller])
    class TestModule:
        pass

    container = PyNestContainer()
    container.add_module(TestModule)
    container.build()
    app = FastAPI()
    RoutesResolver(container, app).register_routes()
    return TestClient(app)


def increment(value):
    return int(value) + 1


class UpperPipe:
    def transform(self, value):
        return value.upper()


TenantHeader = createParamDecorator(
    lambda data, ctx: ctx.switch_to_http().get_request().headers.get(data)
)


ContextAware = createParamDecorator(
    lambda data, ctx: {
        "is_context": isinstance(ctx, ExecutionContext),
        "path": ctx.switch_to_http().get_request().url.path,
    }
)


@Controller("/decorated")
class DecoratedController:
    @Post("/{item_id}")
    def create(
        self,
        item_id=Param("item_id", increment),
        q: str = Query("q", UpperPipe),
        agent: str = Headers("user-agent"),
        body: dict = Body(),
    ):
        return {"item_id": item_id, "q": q, "agent": agent, "body": body}

    @Post("/body-key")
    def body_key(self, name: str = Body("name", UpperPipe)):
        return {"name": name}

    @Get("/{item_id}/request-data")
    def request_data(
        self,
        params: dict = Param(),
        queries: dict = Query(),
        headers: dict = Headers(),
        request: Request = Req(),
        response: Response = Res(),
        ip: str = Ip(),
        host: str = HostParam(),
    ):
        response.headers["x-item-id"] = params["item_id"]
        return {
            "params": params,
            "query": queries["q"],
            "has_host_header": "host" in headers,
            "path": request.url.path,
            "ip": ip,
            "host": host,
        }

    @Get("/custom")
    def custom(
        self,
        tenant: str = TenantHeader("x-tenant-id"),
        context: dict = ContextAware(),
    ):
        return {"tenant": tenant, "context": context}

    @Get("/implicit/{item_id}")
    def implicit(self, item_id: int, q: str):
        return {"item_id": item_id, "q": q}


def test_param_decorators_extract_builtin_sources_and_apply_pipes():
    client = build_client(DecoratedController)

    response = client.post(
        "/decorated/41?q=hello",
        json={"title": "PyNest"},
        headers={"user-agent": "pytest"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "item_id": 42,
        "q": "HELLO",
        "agent": "pytest",
        "body": {"title": "PyNest"},
    }


def test_body_decorator_can_extract_one_body_key():
    client = build_client(DecoratedController)

    response = client.post("/decorated/body-key", json={"name": "ada"})

    assert response.status_code == 200
    assert response.json() == {"name": "ADA"}


def test_request_response_and_whole_collection_decorators():
    client = build_client(DecoratedController)

    response = client.get("/decorated/abc/request-data?q=search")

    assert response.status_code == 200
    assert response.headers["x-item-id"] == "abc"
    assert response.json() == {
        "params": {"item_id": "abc"},
        "query": "search",
        "has_host_header": True,
        "path": "/decorated/abc/request-data",
        "ip": "testclient",
        "host": "testserver",
    }


def test_custom_param_decorator_receives_data_and_execution_context():
    client = build_client(DecoratedController)

    response = client.get("/decorated/custom", headers={"x-tenant-id": "acme"})

    assert response.status_code == 200
    assert response.json() == {
        "tenant": "acme",
        "context": {"is_context": True, "path": "/decorated/custom"},
    }


def test_routes_without_param_decorators_keep_fastapi_binding():
    client = build_client(DecoratedController)

    response = client.get("/decorated/implicit/7?q=plain")

    assert response.status_code == 200
    assert response.json() == {"item_id": 7, "q": "plain"}
