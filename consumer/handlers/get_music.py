from typing import Any, Dict

import msgpack
from aio_pika import ExchangeType
import aio_pika
from sqlalchemy import select
from consumer.logger import correlation_id_ctx
from config.settings import settings
from consumer.storage.db import async_session
from src.model.music import Music
from src.storage.rabbit import channel_pool
import random
from consumer.schema.music import MusicMessage


async def handle_event_music(body: Dict[str, Any]) -> None:
    user_id = body.get('user_id')
    async with async_session() as db:
        
        result = await db.execute(select(Music))
        music_objects = result.scalars().all()

        random_music = {'title': 'default', 'genre': 'classic', 'author': 'Michael', 'streams': '∞'}
        
        if music_objects:
            random_music = random.choice(music_objects).to_dict()

    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange("user_music", ExchangeType.TOPIC, durable=True)
        user_queue = await channel.declare_queue(settings.USER_QUEUE.format(user_id=user_id), durable=True)

        await user_queue.bind(
            exchange,
            settings.USER_QUEUE.format(user_id=user_id),
        )

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(random_music),
                correlation_id=correlation_id_ctx.get(),
            ),
            routing_key=settings.USER_QUEUE.format(user_id=user_id),
        )

