from abc import ABC

from nest import __version__ as version
from nest.cli.templates.abstract_base_template import AbstractBaseTemplate


class RelationalDBTemplate(AbstractBaseTemplate, ABC):
    def __init__(self, name, db_type):
        super().__init__(name, db_type)

    def generate_service_file(self) -> str:
        return f"""from src.{self.name}.{self.name}_model import {self.capitalized_name}
from src.{self.name}.{self.name}_entity import {self.capitalized_name} as {self.capitalized_name}Entity
from nest.core import Injectable
from nest.core.database import DatabaseService
from nest.core.decorators.database import db_request_handler


@Injectable
class {self.capitalized_name}Service:

    def __init__(self, db: DatabaseService):
        self.db = db

    @db_request_handler
    def add_{self.name}(self, {self.name}: {self.capitalized_name}):
        with self.db.session() as session:
            new_{self.name} = {self.capitalized_name}Entity(
                **{self.name}.dict()
            )
            session.add(new_{self.name})
            session.commit()
            return new_{self.name}.id

    @db_request_handler
    def get_{self.name}(self):
        with self.db.session() as session:
            return session.query({self.capitalized_name}Entity).all()
        
    @db_request_handler
    def delete_{self.name}(self, {self.name}_id: int):
        with self.db.session() as session:
            session.query({self.capitalized_name}Entity).filter_by(id={self.name}_id).delete()
            session.commit()
            return {self.name}_id
    
    @db_request_handler
    def update_{self.name}(self, {self.name}_id: int, {self.name}: {self.capitalized_name}):
        with self.db.session() as session:
            session.query({self.capitalized_name}Entity).filter_by(id={self.name}_id).update(
                {self.name}.dict()
            )
            session.commit()
            return {self.name}_id
         """

    def generate_entity_file(self) -> str:
        return f"""from nest.core.database import Base
from sqlalchemy import Column, Integer, String, Float


class {self.capitalized_name}(Base):
    __tablename__ = "{self.name}"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
        """

    def generate_requirements_file(self) -> str:
        return f"""pynest-api=={version}
sqlalchemy>=2.0.36,<3.0.0
python-dotenv>=1.0.1,<2.0.0
    """

    def generate_dockerfile(self) -> str:
        pass

    def generate_orm_config_file(self) -> str:
        base_template = f"""import os
from dotenv import load_dotenv

load_dotenv()
        """

        if self.db_type == "sqlite":
            return f"""{base_template}
DATABASE_CONFIG = dict(
    driver="{self.db_type}",
    database=os.getenv("SQLITE_DB_NAME", "{self.name}_db"),
    create_all=True,
)
            """
        default_port = 5432 if self.db_type == "postgresql" else 3306
        return f"""{base_template}
DATABASE_CONFIG = dict(
    driver="{self.db_type}",
    host=os.getenv("{self.db_type.upper()}_HOST", "localhost"),
    database=os.getenv("{self.db_type.upper()}_DB_NAME", "{self.name}_db"),
    user=os.getenv("{self.db_type.upper()}_USER"),
    password=os.getenv("{self.db_type.upper()}_PASSWORD"),
    port=int(os.getenv("{self.db_type.upper()}_PORT", {default_port})),
    create_all=True,
)
            """


if __name__ == "__main__":
    relational_db_template = RelationalDBTemplate("users", "mysql")
    print(relational_db_template.generate_orm_config_file())
