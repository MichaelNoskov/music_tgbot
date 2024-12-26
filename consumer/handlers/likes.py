from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from consumer.storage.db import async_session
from src.model.music import Music
from src.model.person import Person
from src.model.usermusic import UserMusic
from consumer.logger import logger
from uuid import UUID
import aio_pika
import msgpack
from aio_pika import ExchangeType

from src.storage.rabbit import channel_pool
from config.settings import settings



async def send_answer(liked: bool, user_tg_id):
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange("user_music", ExchangeType.DIRECT, durable=True)
        
        user_queue_name = settings.USER_QUEUE.format(user_id=user_tg_id)
        user_queue = await channel.declare_queue(user_queue_name, durable=True)

        await user_queue.bind(
            exchange,
            user_queue_name,
        )

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb({'liked': liked}),
            ),
            routing_key=user_queue_name,
        )


async def handle_event_like(body: Dict[str, Any]) -> None:
    async with async_session() as db:

        logger.info('Получаем user_id')
        user_id = (await db.execute(select(Person.id).where(Person.telegram_id == str(body.get('user_id'))))).one()[0]
        logger.info(f'user_id: {user_id}')

        relationship = UserMusic(user_id=user_id, music_id=UUID(body.get('music_id')))
        logger.info('relationship')

        db.add(relationship)
        logger.info('commiting')

        try:
            await db.commit()
            await send_answer(True, body.get('user_id'))
        except IntegrityError:
            await db.rollback()


async def handle_event_dislike(body: Dict[str, Any]) -> None:
    async with async_session() as db:


        try:
            user_id = (await db.execute(select(Person.id).where(Person.telegram_id == str(body.get('user_id'))))).one()[0]

            relationship = (
                await db.execute(
                    select(UserMusic).where(UserMusic.user_id == user_id).where(UserMusic.music_id == UUID(body.get('music_id')))
                )
            ).one()[0]
        except:
            return

        await db.delete(relationship)

        try:
            await db.commit()
            await send_answer(False, body.get('user_id'))
        except IntegrityError:
            await db.rollback()
