from typing import Any, Dict

import msgpack
from aio_pika import ExchangeType
import aio_pika
from sqlalchemy import select
from config.settings import settings
from consumer.storage.db import async_session
from src.model.music import Music
from src.storage.rabbit import channel_pool
import random


async def handle_event_music(body: Dict[str, Any]) -> None:

    user_id = body.get('user_id')
    async with async_session() as db:

        result = await db.execute(select(Music))
        music_objects = result.scalars().all()

        random_music = {'title': 'default', 'genre': 'classic', 'author': 'Michael', 'streams': '∞'}

        if music_objects:
            random_music = random.choice(music_objects).to_dict()

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
