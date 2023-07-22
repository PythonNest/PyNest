def generate_entity(name: str, db_type: str) -> str:
    split_name = name.split("_")
    capitalized_name = "".join([word.capitalize() for word in split_name])
    if db_type == "mongodb":
        template = f"""from beanie import Document
        
        
class {capitalized_name}(Document):
    name: str
    
    class Config:
        schema_extra = {{
            "example": {{
                "title": "Example Name",
            }}
        }}
"""
    else:
        template = f"""from orm_config import config
from sqlalchemy import Column, Integer, String, Float
    
    
class {capitalized_name}(config.Base):
    __tablename__ = "{name}"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
        
    """

    return template
