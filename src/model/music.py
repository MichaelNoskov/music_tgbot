from sqlalchemy import Text, String, Integer
from sqlalchemy.orm import Mapped, relationship, mapped_column
from .meta import Base, UUIDMixin
from .author import Author


class Music(Base, UUIDMixin):
    __tablename__ = 'music'

    title: Mapped[str] = mapped_column(nullable=False, index=True)
    author = relationship('Author', back_populates='music', cascade='all, delete-orphan')
    genre: Mapped[str] = mapped_column(String)
    vector: Mapped[int] = mapped_column(Integer)
    file_url: Mapped[str] = mapped_column(nullable=False)  # URL к файлу в MinIO