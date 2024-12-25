from sqlalchemy import Text, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from .meta import Base, UUIDMixin


class Music(Base, UUIDMixin):
    __tablename__ = 'music'

    title: Mapped[str] = mapped_column(String, index=True)
    author = mapped_column(ForeignKey('person.id'), nullable=False)
    genre: Mapped[str] = mapped_column(String)
    streams: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    # vector: Mapped[int] = mapped_column(Integer)
    file_url: Mapped[str] = mapped_column(String, nullable=False)  # URL к файлу в MinIO