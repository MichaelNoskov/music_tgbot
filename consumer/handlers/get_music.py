from typing import Any, Dict

import msgpack
from aio_pika import ExchangeType
import aio_pika
from sqlalchemy import select
from config.settings import settings
from consumer.storage.db import async_session
from src.model.music import Music
from src.model.person import Person
from src.storage.rabbit import channel_pool
import random
from consumer.logger import logger


async def handle_event_music(body: Dict[str, Any]) -> None:

    user_id = body.get('user_id')
    async with async_session() as db:

        logger.info('music Loading...')
        
        result = await db.execute(select(Music))
        music_objects = result.scalars().all()

        random_music = {'title': 'default', 'genre': 'classic', 'author': 'Michael', 'streams': '∞'}
        
        if len(music_objects) > 0:
            mus = music_objects[random.randint(0, len(music_objects)-1)]

            user = (await db.execute(select(Person).where(Person.id == mus.author))).one()[0]

            mus.streams += 1
            await db.commit()

            random_music = {
                'title': mus.title,
                'genre': mus.genre,
                'author': user.username,
                'streams': mus.streams,
                'file_url': mus.file_url
            }

        logger.info(f'Music was found: {random_music}')

    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange("user_music", ExchangeType.DIRECT, durable=True)
        
        user_queue_name = settings.USER_QUEUE.format(user_id=user_id)
        user_queue = await channel.declare_queue(user_queue_name, durable=True)

        await user_queue.bind(
            exchange,
            user_queue_name,
        )

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(random_music),
            ),
            routing_key=user_queue_name,
        )

