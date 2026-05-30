import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Column, Integer, String, inspect, select
from sqlalchemy.orm import DeclarativeBase

from nest.core import Controller, Get, Injectable, Module, PyNestFactory
from nest.core.database import (
    DATABASE_ENGINE,
    DATABASE_OPTIONS,
    DATABASE_SESSION_FACTORY,
    DatabaseModule,
    DatabaseOptions,
    DatabaseService,
)


def test_database_module_for_root_registers_core_providers(tmp_path):
    class LocalBase(DeclarativeBase):
        pass

    database_name = str(tmp_path / "providers")
    configured_database_module = DatabaseModule.for_root(
        driver="sqlite",
        database=database_name,
        base=LocalBase,
        create_all=False,
    )

    @Module(imports=[configured_database_module])
    class AppModule:
        pass

    app = PyNestFactory.create(AppModule)
    options = app.container.get(DATABASE_OPTIONS)
    engine = app.container.get(DATABASE_ENGINE)
    session_factory = app.container.get(DATABASE_SESSION_FACTORY)
    database = app.container.get(DatabaseService)

    assert isinstance(options, DatabaseOptions)
    assert options.driver == "sqlite"
    assert options.config_params == {"db_name": database_name}
    assert database.options is options
    assert database.engine is engine
    assert database.session_factory is session_factory

    asyncio.run(app.close())


def test_database_module_rejects_duplicate_root_registration(tmp_path):
    class LocalBase(DeclarativeBase):
        pass

    @Module(
        imports=[
            DatabaseModule.for_root(
                driver="sqlite",
                database=str(tmp_path / "primary"),
                base=LocalBase,
            ),
            DatabaseModule.for_root(
                driver="sqlite",
                database=str(tmp_path / "secondary"),
                base=LocalBase,
            ),
        ]
    )
    class AppModule:
        pass

    with pytest.raises(RuntimeError, match="DatabaseModule.for_root"):
        PyNestFactory.create(AppModule)


def test_database_module_does_not_create_tables_by_default(tmp_path):
    class LocalBase(DeclarativeBase):
        pass

    class Author(LocalBase):
        __tablename__ = "default_authors"

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, nullable=False)

    @Module(
        imports=[
            DatabaseModule.for_root(
                driver="sqlite",
                database=str(tmp_path / "default-create-all"),
                base=LocalBase,
            )
        ]
    )
    class AppModule:
        pass

    app = PyNestFactory.create(AppModule)
    database = app.container.get(DatabaseService)

    assert "default_authors" not in inspect(database.engine).get_table_names()

    asyncio.run(app.close())


def test_database_service_runs_sync_lifecycle_hooks():
    events = []

    class Metadata:
        def create_all(self, bind):
            events.append(("create_all", bind))

    class LocalBase:
        metadata = Metadata()

    class Engine:
        def dispose(self):
            events.append("dispose")

    engine = Engine()
    options = DatabaseOptions(
        driver="sqlite",
        config_params={"db_name": "lifecycle"},
        base=LocalBase,
        create_all=True,
    )
    service = DatabaseService(options, engine, session_factory=lambda: object())

    service.on_module_init()
    service.on_module_destroy()

    assert events == [("create_all", engine), "dispose"]


def test_database_service_session_rolls_back_and_closes_on_error():
    events = []

    class Session:
        def rollback(self):
            events.append("rollback")

        def close(self):
            events.append("close")

    options = DatabaseOptions(
        driver="sqlite",
        config_params={"db_name": "sessions"},
        create_all=False,
    )
    service = DatabaseService(options, engine=object(), session_factory=Session)

    with pytest.raises(ValueError, match="boom"):
        with service.session() as session:
            assert isinstance(session, Session)
            raise ValueError("boom")

    assert events == ["rollback", "close"]


def test_database_service_can_be_replaced_by_app_provider(tmp_path):
    class LocalBase(DeclarativeBase):
        pass

    class FakeDatabaseService:
        def session(self):
            return "fake-session"

    fake_database = FakeDatabaseService()

    @Injectable
    class UsesDatabase:
        def __init__(self, db: DatabaseService):
            self.db = db

    @Module(
        imports=[
            DatabaseModule.for_root(
                driver="sqlite",
                database=str(tmp_path / "replace"),
                base=LocalBase,
                create_all=False,
            )
        ],
        providers=[
            {"provide": DatabaseService, "useValue": fake_database},
            UsesDatabase,
        ],
    )
    class AppModule:
        pass

    app = PyNestFactory.create(AppModule)

    assert app.container.get(DatabaseService) is fake_database
    assert app.container.get(UsesDatabase).db is fake_database

    asyncio.run(app.close())


def test_database_module_powers_feature_module_through_http_e2e(tmp_path):
    class LocalBase(DeclarativeBase):
        pass

    class Author(LocalBase):
        __tablename__ = "authors"

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, nullable=False)

    @Injectable
    class AuthorService:
        def __init__(self, db: DatabaseService):
            self.db = db

        def create_and_list(self):
            with self.db.session() as session:
                session.add(Author(name="Le Guin"))
                session.commit()

            with self.db.session() as session:
                authors = session.query(Author).order_by(Author.name).all()
                return [author.name for author in authors]

    @Controller("/authors", tag="authors")
    class AuthorController:
        def __init__(self, service: AuthorService):
            self.service = service

        @Get("/")
        def list_authors(self):
            return {"authors": self.service.create_and_list()}

    @Module(controllers=[AuthorController], providers=[AuthorService])
    class AuthorModule:
        pass

    @Module(
        imports=[
            DatabaseModule.for_root(
                driver="sqlite",
                database=str(tmp_path / "authors"),
                base=LocalBase,
                create_all=True,
            ),
            AuthorModule,
        ]
    )
    class AppModule:
        pass

    app = PyNestFactory.create(AppModule)
    database = app.container.get(DatabaseService)

    assert "authors" in inspect(database.engine).get_table_names()

    with TestClient(app.get_server()) as client:
        response = client.get("/authors")

    assert response.status_code == 200
    assert response.json() == {"authors": ["Le Guin"]}


def test_async_database_module_creates_tables_and_runs_queries(tmp_path):
    class LocalBase(DeclarativeBase):
        pass

    class Author(LocalBase):
        __tablename__ = "async_authors"

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, nullable=False)

    @Module(
        imports=[
            DatabaseModule.for_root(
                driver="sqlite",
                database=str(tmp_path / "async-authors"),
                base=LocalBase,
                async_mode=True,
                create_all=True,
            )
        ]
    )
    class AppModule:
        pass

    app = PyNestFactory.create(AppModule)
    database = app.container.get(DatabaseService)

    async def scenario():
        async with database.session() as session:
            session.add(Author(name="Butler"))
            await session.commit()

        async with database.session() as session:
            result = await session.execute(select(Author.name))
            return result.scalars().all()

    assert asyncio.run(scenario()) == ["Butler"]

    asyncio.run(app.close())
