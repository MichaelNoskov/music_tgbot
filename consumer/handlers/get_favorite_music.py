from typing import Any, Dict

import msgpack
from aio_pika import ExchangeType
import aio_pika
from sqlalchemy import select
from config.settings import settings
from consumer.storage.db import async_session
from src.model.music import Music
from src.model.person import Person
from src.model.usermusic import UserMusic
from src.storage.rabbit import channel_pool
from consumer.logger import logger


async def handle_event_favorite_music(body: Dict[str, Any]) -> None:

    user_tg_id = str(body.get('user_id'))
    async with async_session() as db:

        logger.info('music Loading...')

        user_id = (await db.execute(select(Person.id).where(Person.telegram_id == user_tg_id))).scalars().first()

        music_ids = (await db.execute(select(UserMusic.music_id).where(UserMusic.user_id == user_id))).scalars().all()

        logger.info(music_ids)

        music = {'music': []}

        for mus_id in music_ids:
            mus = (await db.execute(select(Music).where(Music.id == mus_id))).scalars().first()
            music['music'].append(
                {
                    'title': mus.title,
                    'genre': mus.genre,
                    'author': (await db.execute(select(Person.username).where(Person.id == mus.author)))
                    .scalars()
                    .first(),
                    'streams': mus.streams,
                    'file_url': mus.file_url,
                    'music_id': str(mus.id),
                    'liked': True,
                }
            )

        logger.info(f'Music was found: {music}')

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
                msgpack.packb(music),
            ),
            routing_key=user_queue_name,
        )
