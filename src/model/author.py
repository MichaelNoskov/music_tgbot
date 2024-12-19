from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .meta import Base, UUIDMixin


class Author(Base, UUIDMixin):
    __tablename__ = 'author'

    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(String)