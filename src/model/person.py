from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .meta import Base, UUIDMixin


class Person(Base, UUIDMixin):
    __tablename__ = 'person'

    telegram_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(String)
    # favorite_music: Mapped[List[Music]] = relationship(secondary='usermusic')