from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .meta import Base


class Person(Base):
    __tablename__ = 'person'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(String)
    # favorite_music: Mapped[List[Music]] = relationship(secondary='usermusic')
