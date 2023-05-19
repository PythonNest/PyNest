def generate_entity(name: str) -> str:
    split_name = name.split("_")
    capitalized_name = "".join([word.capitalize() for word in split_name])
    template = f"""from orm_config import config
from sqlalchemy import Column, Integer, String, Float


class {capitalized_name}(config.Base):
    __tablename__ = "{name}"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    
"""

    return template
