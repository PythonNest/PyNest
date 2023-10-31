AUTH_ENTITY_TEMPLATE = """from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from orm_config import config


class User(config.Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

"""
