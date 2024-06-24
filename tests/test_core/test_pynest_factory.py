import pytest
from fastapi import FastAPI

from nest.core import PyNestFactory  # Replace 'your_module' with the actual module name
from tests.test_core import test_container, test_module, test_server


def test_create_server(test_server):
    assert isinstance(test_server, FastAPI)
    assert test_server.title == "Test Server"
    assert test_server.description == "This is a test server"
    assert test_server.version == "1.0.0"
    assert test_server.debug is True


def test_e2e(test_module):
    app = PyNestFactory.create(
        test_module,
        title="Test Server",
        description="This is a test server",
        version="1.0.0",
        debug=True,
    )
    http_server = app.get_server()
    assert isinstance(http_server, FastAPI)
    assert http_server.title == "Test Server"
    assert http_server.description == "This is a test server"
    assert http_server.version == "1.0.0"
    assert http_server.debug is True
