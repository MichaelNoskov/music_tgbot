from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from .meta import Base
from .meta import UUIDMixin


class UserMusic(Base, UUIDMixin):
    __tablename__ = 'usermusic'
    
    user_id = mapped_column('person', ForeignKey('person.id'), nullable=False)
    music_id = mapped_column('music', ForeignKey('music.id'), nullable=False)