import os

import pytest
from nest.core.database.orm_config import ConfigFactory, SQLiteConfig, PostgresConfig, MySQLConfig
from nest.core.database.base_orm import OrmService


@pytest.fixture(scope="module")
def orm_service():
    return OrmService(
        db_type="sqlite",
        config_params=dict(
            db_name=os.getenv("SQLITE_DB_NAME", "default_nest_db")
        ),
    )


@pytest.fixture(scope="module")
def sqlite_config():
    return SQLiteConfig("test")


@pytest.fixture(scope="module")
def postgres_config():
    return PostgresConfig("test", "test", "test", "test", "test")


@pytest.fixture(scope="module")
def mysql_config():
    return MySQLConfig("test", "test", "test", "test", "test")


def test_orm_service_definition(orm_service):
    assert orm_service.Base
    assert orm_service.config
    assert orm_service.config_url
    assert orm_service.engine


def test_orm_service_config_url(orm_service):
    config_url = orm_service.config_url
    assert config_url == "sqlite:///default_nest_db.db"


def test_orm_service_engine(orm_service):
    engine = orm_service.engine
    assert engine


