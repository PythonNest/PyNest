import pytest

from nest.core import PyNestApp
from tests.test_core import test_container, test_resolver
from tests.test_core.test_pynest_factory import test_server


@pytest.fixture
def pynest_app(test_container, test_server):
    return PyNestApp(container=test_container, http_server=test_server)


def test_is_listening_property(pynest_app):
    assert not pynest_app.is_listening
    pynest_app._is_listening = (
        True  # Directly modify the protected attribute for testing
    )
    assert pynest_app.is_listening


def test_get_server_returns_http_server(pynest_app, test_server):
    assert pynest_app.get_server() == test_server


def test_register_routes_calls_register_routes_on_resolver(pynest_app, test_resolver):
    pynest_app.routes_resolver = test_resolver
    pynest_app.register_routes()
    assert pynest_app.get_server().routes
