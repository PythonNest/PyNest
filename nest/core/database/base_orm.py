from sqlalchemy.ext.declarative import declarative_base
from nest.core.database.orm_config import ConfigFactory
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker, Session


class OrmService:

    def __init__(self, db_type: str = "postgresql", config_params: dict = None):
        self.Base = declarative_base()
        self.config = ConfigFactory(db_type=db_type).get_config()
        self.config_url = self.config(**config_params).get_engine_url()
        self.engine = create_engine(self.config_url)

    def create_all(self):
        self.Base.metadata.create_all(bind=self.engine)

    def drop_all(self):
        self.Base.metadata.drop_all(bind=self.engine)

    def get_db(self) -> Session:
        try:
            session = sessionmaker(bind=self.engine)
            return session()
        except Exception as e:
            raise e
