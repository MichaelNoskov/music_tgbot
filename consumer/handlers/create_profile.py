from typing import Any, Dict

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from consumer.storage.db import async_session
from src.model.person import Person
from consumer.logger import logger
import msgpack
from aio_pika import ExchangeType
import aio_pika
from sqlalchemy import select
from config.settings import settings
from consumer.storage.db import async_session
from src.model.person import Person
from src.storage.rabbit import channel_pool
from consumer.logger import logger


async def handle_event_profile(body: Dict[str, Any]) -> None:

    user_tg_id = body.get('user_id')
    async with async_session() as db:
        
        new_user = (await db.execute(select(Person.id).where(Person.telegram_id == str(user_tg_id)))).scalars().first()
        logger.info(f'user found: {new_user}')

        if new_user is None:
            new_user = Person(
                username=body.get('username'),
                description=body.get('description'),
                telegram_id=str(user_tg_id),
            )
            db.add(new_user)
            
            try:
                await db.commit()
                logger.info(f'User created: {new_user}')
            except IntegrityError:
                await db.rollback()
                return

    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange('user_music', ExchangeType.DIRECT, durable=True)
        
        user_queue_name = settings.USER_QUEUE.format(user_id=user_tg_id)
        user_queue = await channel.declare_queue(user_queue_name, durable=True)

        await user_queue.bind(
            exchange,
            user_queue_name,
        )

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(
                    {'authorized': 'yes'}
                ),
            ),
            routing_key=user_queue_name,
        )
        
    
