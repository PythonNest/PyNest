from examples.nest_products.orm_config import config
from sqlalchemy import Column, Integer, String


class Test(config.Base):
    __tablename__ = "test"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    
