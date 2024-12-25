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
import random
from consumer.logger import logger


async def handle_event_music(body: Dict[str, Any]) -> None:

    user_tg_id = body.get('user_id')
    async with async_session() as db:

        logger.info('music Loading...')
        
        result = await db.execute(select(Music))
        music_objects = result.scalars().all()

        random_music = {'title': 'default', 'genre': 'classic', 'author': 'Michael', 'streams': '∞'}
        
        if len(music_objects) > 0:
            mus = music_objects[random.randint(0, len(music_objects)-1)]

            author_name = (await db.execute(select(Person.username).where(Person.id == mus.author))).scalars().first()
            logger.info('author')

            user_id = (await db.execute(select(Person.id).where(Person.telegram_id == str(user_tg_id)))).scalars().first()
            logger.info('user')
            if user_id is None:
                liked = False
            else:
                user_id = user_id
                logger.info(f'user: {type(user_id)}')
                liked = (await db.execute(select(UserMusic).where(UserMusic.user_id == user_id).where(UserMusic.music_id == mus.id))).scalars().first() is not None
                logger.info('liked')

            mus.streams += 1
            await db.commit()

            random_music = {
                'title': mus.title,
                'genre': mus.genre,
                'author': author_name,
                'streams': mus.streams,
                'file_url': mus.file_url,
                'music_id': str(mus.id),
                'liked': liked,
            }

        logger.info(f'Music was found: {random_music}')

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
                msgpack.packb(random_music),
            ),
            routing_key=user_queue_name,
        )

