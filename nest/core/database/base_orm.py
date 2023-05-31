from sqlalchemy.ext.declarative import declarative_base
from nest.core.database.orm_config import ConfigFactory
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker, Session


class OrmService:
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

    def __init__(self, db_type: str = "postgresql", config_params: dict = None):
        """
        Initializes the OrmService instance.

        Args:
            db_type (str, optional): The type of database. Defaults to "postgresql".
            config_params (dict, optional): Configuration parameters specific to the chosen database type.
                                            Defaults to None.
        """
        self.Base = declarative_base()
        self.config = ConfigFactory(db_type=db_type).get_config()
        self.config_url = self.config(**config_params).get_engine_url()
        self.engine = create_engine(self.config_url)

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
