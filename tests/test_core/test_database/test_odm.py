import os

import pytest

from nest.core.database.odm_config import ConfigFactory, MongoDBConfig
from nest.core.database.odm_provider import OdmProvider


@pytest.fixture(scope="module")
def odm_service():
    return OdmProvider(
        db_type="mongodb",
        config_params={
            "db_name": "db_name",
            "host": "host",
            "user": "user",
            "password": "password",
            "port": "port",
        },
        document_models=[],
    )


@pytest.fixture(scope="module")
def mongodb_config():
    return MongoDBConfig(
        db_name="db_name", host="host", user="user", password="password", port="port"
    )


def test_odm_service_definition(odm_service):
    assert odm_service.config
    assert odm_service.config_url
    assert odm_service.document_models == []


def test_odm_service_config_url(odm_service):
    config_url = odm_service.config_url
    assert config_url == "mongodb://user:password@host:port"


def test_mongo_config_definition(mongodb_config):
    assert mongodb_config
    assert mongodb_config.get_engine_url
