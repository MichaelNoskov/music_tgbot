from typing import Any, Dict

from sqlalchemy import select

from consumer.storage.db import async_session
from src.model.music import Music
from src.model.person import Person
from consumer.logger import logger


async def handle_event_upload_music(body: Dict[str, Any]) -> None:
    async with async_session() as db:

        user = (await db.execute(select(Person).where(Person.id == body.get('user_id')))).one()[0]

        new_music = Music(
            title=body.get('title'),
            genre=body.get('genre'),
            file_url=body.get('file_url'),
            author=user
        )
        db.add(new_music)
        await db.commit()

        logger.info('Music uploaded: %s', body)
