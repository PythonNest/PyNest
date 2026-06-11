# tests/test_engine/unit/test_http_adapter_base.py
from __future__ import annotations

import inspect
import pytest


def _make_concrete_adapter():
    """Return a concrete AbstractHttpAdapter subclass with all methods implemented."""
    from nest.engine.http_adapter import AbstractHttpAdapter

    class ConcreteAdapter(AbstractHttpAdapter):
        def _create_instance(self):
            return object()

        async def close(self):
            pass

        def add_route(self, spec):
            pass

        def add_websocket_route(self, path, endpoint):
            pass

        def use(self, middleware, **opts):
            pass

        def enable_cors(self, **opts):
            pass

        def register_startup_hook(self, fn):
            pass

        def register_shutdown_hook(self, fn):
            pass

        def register_exception_handler(self, exc_type, handler):
            pass

        def get_request_method(self, req):
            return "GET"

        def get_request_url(self, req):
            return "/test"

        def get_request_hostname(self, req):
            return "localhost"

        def get_request_headers(self, req):
            return {}

        def get_request_client_ip(self, req):
            return "127.0.0.1"

        def reply(self, res, body, status_code=None):
            pass

        def set_header(self, res, name, value):
            pass

        def is_headers_sent(self, res):
            return False

        def redirect(self, res, url, status_code=302):
            pass

    return ConcreteAdapter


def test_abstract_adapter_cannot_be_instantiated_directly():
    from nest.engine.http_adapter import AbstractHttpAdapter
    with pytest.raises(TypeError):
        AbstractHttpAdapter()  # type: ignore[abstract]


def test_concrete_adapter_requires_all_abstract_methods():
    from nest.engine.http_adapter import AbstractHttpAdapter

    class Incomplete(AbstractHttpAdapter):
        def _create_instance(self):
            return object()
        # missing all other abstract methods

    with pytest.raises(TypeError):
        Incomplete()


def test_get_http_server_returns_instance():
    cls = _make_concrete_adapter()
    adapter = cls()
    assert adapter.get_http_server() is not None


def test_get_type_strips_adapter_suffix():
    cls = _make_concrete_adapter()
    adapter = cls()
    # Class is named "ConcreteAdapter" → type is "concrete"
    assert adapter.get_type() == "concrete"


def test_get_type_no_adapter_suffix():
    from nest.engine.http_adapter import AbstractHttpAdapter

    cls = _make_concrete_adapter()

    class MyEngine(cls):
        pass

    # Rename for the test
    MyEngine.__name__ = "MyEngine"
    adapter = MyEngine()
    assert adapter.get_type() == "myengine"


def test_adapter_instance_passthrough():
    cls = _make_concrete_adapter()
    sentinel = object()
    adapter = cls(instance=sentinel)
    assert adapter.get_http_server() is sentinel


def test_all_abstract_methods_are_listed():
    """Verify the ABC enforces the full expected contract surface."""
    from nest.engine.http_adapter import AbstractHttpAdapter

    abstract_methods = {
        name
        for name, method in inspect.getmembers(AbstractHttpAdapter)
        if getattr(method, "__isabstractmethod__", False)
    }
    expected = {
        "_create_instance", "close", "add_route", "add_websocket_route",
        "use", "enable_cors", "register_startup_hook", "register_shutdown_hook",
        "register_exception_handler", "get_request_method", "get_request_url",
        "get_request_hostname", "get_request_headers", "get_request_client_ip",
        "reply", "set_header", "is_headers_sent", "redirect",
    }
    assert abstract_methods == expected
