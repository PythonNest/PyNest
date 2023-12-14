from orm_config import config
from sqlalchemy import Column, Integer, String, Float


class Product(config.Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    price = Column(Float)
    description = Column(String(1000))
