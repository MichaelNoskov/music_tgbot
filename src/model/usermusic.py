from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped
from .meta import Base


class UserMusic(Base):
    __tablename__ = 'usermusic'
    
    user_id = Mapped(Integer, ForeignKey('user.id'), primary_key=True)
    music_id = Mapped(Integer, ForeignKey('music.id'), primary_key=True)