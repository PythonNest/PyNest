from nest.core.database.orm_config import ConfigFactory, AsyncConfigFactory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager
from typing import AsyncGenerator


class Base(DeclarativeBase):
    """
    Base class for ORM models.

    """

    pass


class OrmProvider:
    """
    Provides an interface for working with an ORM (Object-Relational Mapping) service.

    Args:
        db_type (str, optional): The type of database. Defaults to "postgresql".
        config_params (dict, optional): Configuration parameters specific to the chosen database type.
                                        Defaults to None.

    Attributes:
        Base: The declarative base class for defining ORM models.
        config: The configuration factory for the chosen database type.
        config_url: The URL generated from the database configuration parameters.
        engine: The SQLAlchemy engine for database connection.

    """

    def __init__(
        self, db_type: str = "postgresql", config_params: dict = None, **kwargs
    ):
        """
        Initializes the OrmService instance.

        Args:
            db_type (str, optional): The type of database. Defaults to "postgresql".
            config_params (dict, optional): Configuration parameters specific to the chosen database type.
                                            Defaults to None.
        """
        self.Base: DeclarativeBase = Base()
        self.config = ConfigFactory(db_type=db_type).get_config()
        self.config_url = self.config(**config_params).get_engine_url()
        self.engine = create_engine(self.config_url, **kwargs)

    def create_all(self):
        """
        Creates all the tables defined by the ORM models.

        Raises:
            Exception: If there's an error creating the tables.
        """
        self.Base.metadata.create_all(bind=self.engine)

    def drop_all(self):
        """
        Drops all the tables defined by the ORM models.

        Raises:
            Exception: If there's an error dropping the tables.
        """
        self.Base.metadata.drop_all(bind=self.engine)

    def get_db(self) -> Session:
        """
        Returns a SQLAlchemy Session object for database operations.

        Returns:
            Session: A SQLAlchemy Session object.

        Raises:
            Exception: If there's an error creating the session.
        """
        try:
            session = sessionmaker(bind=self.engine)
            return session()
        except Exception as e:
            raise e


class AsyncOrmProvider:
    """
    Provides ORM services for asynchronous database operations.

    Attributes:
        Base (DeclarativeBase): The base class for declarative class definitions.
        config (function): Configuration function for the database.
        config_url (str): Database connection URL.
        engine: Asynchronous engine for the database.
        Session: Asynchronous sessionmaker for creating sessions.
    """

    def __init__(
        self, db_type: str = "postgresql", config_params: dict = None, **kwargs
    ):
        """
        Initializes the AsyncOrmProvider with specified database configuration.

        Args:
            db_type (str): Type of database (e.g., 'postgresql').
            config_params (dict): Configuration parameters for the database.
            **kwargs: Additional keyword arguments.
        """
        self.Base: DeclarativeBase = Base
        self.config = AsyncConfigFactory(db_type=db_type).get_config()
        self.config_url = self.config(**config_params).get_engine_url()
        self.engine = create_async_engine(self.config_url, echo=True, **kwargs)
        self.Session = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def create_all(self):
        """
        Creates all tables in the database asynchronously.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)

    async def drop_all(self):
        """
        Drops all tables in the database asynchronously.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.drop_all)

    async def get_db(self) -> AsyncSession:
        db = self.Session()
        try:
            yield db
        finally:
            await db.close()

    @asynccontextmanager
    async def get_self_db(self) -> AsyncGenerator[AsyncSession, None]:
        db = self.Session()
        try:
            yield db
        finally:
            await db.close()
