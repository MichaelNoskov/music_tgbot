from .base import BaseMessage

class MusicMessage(BaseMessage):
    action: str
    user_id: int
