from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from consumer.storage.db import async_session
from src.model.music import Music
from src.model.person import Person
from consumer.logger import logger


async def handle_event_upload_music(body: Dict[str, Any]) -> None:
    async with async_session() as db:

        user = (await db.execute(select(Person).where(Person.telegram_id == str(body.get('user_id'))))).one()[0]

        new_music = Music(
            title=body.get('title'),
            author=user.id,
            genre=body.get('genre'),
            # streams=0,
            file_url=body.get('file_url'),
        )
        db.add(new_music)

        try:
            await db.commit()
            logger.info(f'Music uploaded: {new_music}')
        except IntegrityError:
            logger.info('Music already exists')
            await db.rollback()
