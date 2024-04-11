from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..config import config


class User(config.Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
