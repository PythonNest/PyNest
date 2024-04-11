from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..config import config


class Example(config.Base):
    __tablename__ = "example"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
