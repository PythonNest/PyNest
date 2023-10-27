from nest.core.database.orm_config import config 
from sqlalchemy import Column, Integer, String


class User(config.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
