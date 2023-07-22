import os

import pytest
from nest.core.database.odm_config import (
    ConfigFactory,
    MongoDBConfig,
)

from nest.core.database.base_odm import OdmService


@pytest.fixture(scope="module")
def odm_service():
    return OdmService(
        db_type="mongodb",
        config_params={
            "db_name": "test",
            "host": "test",
            "port": "test",
        },
        document_models=[],
    )


@pytest.fixture(scope="module")
def mongodb_config():
    return MongoDBConfig("test", "test", "test")


def test_odm_service_definition(odm_service):
    assert odm_service.config
    assert odm_service.config_url
    assert odm_service.document_models == []


def test_odm_service_config_url(odm_service):
    config_url = odm_service.config_url
    assert config_url == "mongodb://test:test"
