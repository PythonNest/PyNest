import os

import pytest

from nest.core.database.orm_config import ConfigFactory
from nest.core.database.orm_provider import OrmProvider


@pytest.fixture(scope="module")
def config_factory():
    return ConfigFactory


def test_config_factory_definition(config_factory):
    assert config_factory
    assert config_factory.get_config


@pytest.fixture(scope="module")
def sqlite_config_factory(config_factory):
    config = config_factory(db_type="sqlite").get_config()
    params = dict(db_name=os.getenv("SQLITE_DB_NAME", "default_nest_db"))
    return config(**params)


@pytest.fixture(scope="module")
def postgres_config_factory(config_factory):
    config = config_factory(db_type="postgresql").get_config()
    params = dict(
        db_name=os.getenv("POSTGRES_DB_NAME", "default_nest_db"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )
    return config(**params)


@pytest.fixture(scope="module")
def mysql_config_factory(config_factory):
    config = config_factory(db_type="mysql").get_config()
    params = dict(
        db_name=os.getenv("MYSQL_DB_NAME", "default_nest_db"),
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "root"),
        port=os.getenv("MYSQL_PORT", "3306"),
    )
    return config(**params)


def test_sqlite_url(sqlite_config_factory):
    config_url = sqlite_config_factory.get_engine_url()
    assert config_url == "sqlite:///default_nest_db.db"


def test_postgres_url(postgres_config_factory):
    config_url = postgres_config_factory.get_engine_url()
    assert (
        config_url
        == "postgresql+psycopg2://postgres:postgres@localhost:5432/default_nest_db"
    )


def test_mysql_url(mysql_config_factory):
    config_url = mysql_config_factory.get_engine_url()
    assert (
        config_url == "mysql+mysqlconnector://root:root@localhost:3306/default_nest_db"
    )


@pytest.fixture(scope="module")
def sqlite_orm_service():
    return OrmProvider(
        db_type="sqlite",
        config_params=dict(db_name=os.getenv("SQLITE_DB_NAME", "default_nest_db")),
    )


@pytest.fixture(scope="module")
def postgres_orm_service():
    return OrmProvider(
        db_type="postgresql",
        config_params=dict(
            db_name=os.getenv("POSTGRES_DB_NAME", "default_nest_db"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            port=os.getenv("POSTGRES_PORT", "5432"),
        ),
    )


@pytest.fixture(scope="module")
def mysql_orm_service():
    return OrmProvider(
        db_type="mysql",
        config_params=dict(
            db_name=os.getenv("MYSQL_DB_NAME", "default_nest_db"),
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "root"),
            port=os.getenv("MYSQL_PORT", "3306"),
        ),
    )
