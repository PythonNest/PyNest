from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, Optional, Type

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from nest.common.provider import InjectionToken
from nest.core.decorators.module import Module
from nest.core.database.orm_config import AsyncConfigFactory, ConfigFactory
from nest.core.database.orm_provider import Base

DATABASE_OPTIONS = InjectionToken(
    "DATABASE_OPTIONS", "Normalized DatabaseModule.for_root options"
)
DATABASE_ENGINE = InjectionToken("DATABASE_ENGINE", "SQLAlchemy engine")
DATABASE_SESSION_FACTORY = InjectionToken(
    "DATABASE_SESSION_FACTORY", "SQLAlchemy session factory"
)


@dataclass(frozen=True)
class DatabaseOptions:
    driver: str
    config_params: Dict[str, Any]
    async_mode: bool = False
    engine_params: Dict[str, Any] = field(default_factory=dict)
    session_params: Dict[str, Any] = field(default_factory=dict)
    create_all: bool = False
    base: Type[Any] = Base


class DatabaseService:
    """Lifecycle-aware SQLAlchemy service registered by DatabaseModule."""

    def __init__(
        self,
        options: DatabaseOptions,
        engine: Any,
        session_factory: Any,
    ) -> None:
        self.options = options
        self.engine = engine
        self.session_factory = session_factory
        self.Base = options.base

    def on_module_init(self):
        if not self.options.create_all:
            return None
        return self.create_all()

    def on_module_destroy(self):
        result = self.engine.dispose()
        return result

    def create_all(self):
        if self.options.async_mode:
            return self._create_all_async()
        self.Base.metadata.create_all(bind=self.engine)
        return None

    async def _create_all_async(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)

    def drop_all(self):
        if self.options.async_mode:
            return self._drop_all_async()
        self.Base.metadata.drop_all(bind=self.engine)
        return None

    async def _drop_all_async(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.drop_all)

    def session(self):
        if self.options.async_mode:
            return self._async_session()
        return self._sync_session()

    def get_session(self):
        return self.session()

    def get_db(self):
        if self.options.async_mode:
            return self._async_db()
        return self._sync_db()

    @contextmanager
    def _sync_session(self) -> Generator[Session, None, None]:
        db = self.session_factory()
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _sync_db(self) -> Session:
        return self.session_factory()

    @asynccontextmanager
    async def _async_session(self) -> AsyncSession:
        db = self.session_factory()
        try:
            yield db
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()

    async def _async_db(self):
        db = self.session_factory()
        try:
            yield db
        finally:
            await db.close()


def create_database_engine(options: DatabaseOptions):
    config_factory = AsyncConfigFactory if options.async_mode else ConfigFactory
    engine_factory = create_async_engine if options.async_mode else create_engine
    config_class = config_factory(db_type=options.driver).get_config()
    config_url = config_class(**options.config_params).get_engine_url()
    return engine_factory(config_url, **options.engine_params)


def create_database_session_factory(options: DatabaseOptions, engine: Any):
    if options.async_mode:
        session_params = {"expire_on_commit": False, "class_": AsyncSession}
        session_params.update(options.session_params)
        return async_sessionmaker(engine, **session_params)
    return sessionmaker(engine, **options.session_params)


def create_database_service(
    options: DatabaseOptions,
    engine: Any,
    session_factory: Any,
) -> DatabaseService:
    return DatabaseService(options, engine, session_factory)


@Module(imports=[], providers=[], exports=[])
class DatabaseModule:
    @classmethod
    def for_root(
        cls,
        driver: str = "postgresql",
        *,
        database: Optional[str] = None,
        db_name: Optional[str] = None,
        config_params: Optional[Dict[str, Any]] = None,
        host: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        port: Optional[int] = None,
        async_mode: bool = False,
        engine_params: Optional[Dict[str, Any]] = None,
        session_params: Optional[Dict[str, Any]] = None,
        create_all: bool = False,
        base: Type[Any] = Base,
        is_global: bool = True,
        **extra_config: Any,
    ):
        normalized_config = _normalize_config_params(
            config_params=config_params,
            database=database,
            db_name=db_name,
            host=host,
            user=user,
            password=password,
            port=port,
            extra_config=extra_config,
        )
        options = DatabaseOptions(
            driver=driver,
            config_params=normalized_config,
            async_mode=async_mode,
            engine_params=engine_params or {},
            session_params=session_params or {},
            create_all=create_all,
            base=base,
        )

        providers = [
            {"provide": DATABASE_OPTIONS, "useValue": options},
            {
                "provide": DATABASE_ENGINE,
                "useFactory": create_database_engine,
                "inject": [DATABASE_OPTIONS],
            },
            {
                "provide": DATABASE_SESSION_FACTORY,
                "useFactory": create_database_session_factory,
                "inject": [DATABASE_OPTIONS, DATABASE_ENGINE],
            },
            {
                "provide": DatabaseService,
                "useFactory": create_database_service,
                "inject": [
                    DATABASE_OPTIONS,
                    DATABASE_ENGINE,
                    DATABASE_SESSION_FACTORY,
                ],
            },
        ]

        module_name = _configured_module_name(driver=driver, async_mode=async_mode)
        configured_module = type(module_name, (cls,), {})
        setattr(configured_module, "__pynest_database_root__", True)
        return Module(
            imports=[],
            providers=providers,
            exports=[
                DATABASE_OPTIONS,
                DATABASE_ENGINE,
                DATABASE_SESSION_FACTORY,
                DatabaseService,
            ],
            is_global=is_global,
        )(configured_module)


def _normalize_config_params(
    *,
    config_params: Optional[Dict[str, Any]],
    database: Optional[str],
    db_name: Optional[str],
    host: Optional[str],
    user: Optional[str],
    password: Optional[str],
    port: Optional[int],
    extra_config: Dict[str, Any],
) -> Dict[str, Any]:
    normalized = dict(config_params or {})

    database_name = db_name if db_name is not None else database
    if database_name is not None and "db_name" not in normalized:
        normalized["db_name"] = database_name

    for key, value in {
        "host": host,
        "user": user,
        "password": password,
        "port": port,
    }.items():
        if value is not None and key not in normalized:
            normalized[key] = value

    for key, value in extra_config.items():
        if value is not None and key not in normalized:
            normalized[key] = value

    return normalized


def _configured_module_name(driver: str, async_mode: bool) -> str:
    prefix = "Async" if async_mode else ""
    normalized_driver = "".join(part.capitalize() for part in driver.split("_"))
    return f"{prefix}{normalized_driver}DatabaseModule"
