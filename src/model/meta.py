from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from uuid import UUID, uuid4

class Base(DeclarativeBase):
    pass

class UUIDMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)