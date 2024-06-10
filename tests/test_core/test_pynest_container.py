import pytest

from nest.core import Module, PyNestContainer
from tests.test_core import test_module


@pytest.fixture(scope="module")
def container():
    # Since PyNestContainer is a singleton, we clear its state before each test to ensure test isolation
    PyNestContainer()._instance = None
    return PyNestContainer()


def test_singleton_pattern(container):
    second_container = PyNestContainer()
    assert (
        container is second_container
    ), "PyNestContainer should implement the singleton pattern"


def test_add_module(container, test_module):
    result = container.add_module(test_module)
    assert result["inserted"] is True, "Module should be added successfully"
    module_ref = result["module_ref"]
    assert module_ref is not None, "Module reference should not be None"
    assert container.modules.has(
        module_ref.token
    ), "Module should be added to the container"
