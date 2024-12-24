from typing import Any, Dict

from sqlalchemy.exc import IntegrityError

from consumer.storage.db import async_session
from src.model.person import Person
from consumer.logger import logger


async def handle_event_profile(body: Dict[str, Any]) -> None:
    async with async_session() as db:

        new_user = Person(
            username=body.get('username'),
            description=body.get('description'),
            # id=int(body.get('id')),
        )
        db.add(new_user)

        try:
            await db.commit()
            logger.info(f'User created: {new_user}')
        except IntegrityError:
            logger.info('User already exists')
            await db.rollback()
