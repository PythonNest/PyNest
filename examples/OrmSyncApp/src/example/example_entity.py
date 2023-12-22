from config import config
from sqlalchemy import Column, Integer, String, Float
    
    
class Example(config.Base):
    __tablename__ = "example"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

