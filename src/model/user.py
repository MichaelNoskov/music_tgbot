from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .meta import Base, UUIDMixin
from .music import Music

class User(Base, UUIDMixin):
    __tablename__ = 'user'

    username: Mapped[str] = mapped_column(index=True)