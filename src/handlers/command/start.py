import msgpack
import aio_pika
from aiogram.filters import Command
from aiogram.types import Message

from src.handlers.command.router import router
from src.templates.env import render
from src.storage.rabbit import channel_pool
from config.settings import settings


@router.message(Command('start'))
async def menu(message: Message) -> None:
    await message.answer(render('start.jinja2'))
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange('user_music', aio_pika.ExchangeType.TOPIC, durable=True)
        queue = await channel.declare_queue(
            settings.USER_QUEUE.format(user_id=message.from_user.id),
            durable=True
        )
        user_queue = await channel.declare_queue(
            'user_messages',
            durable=True
        )

        await queue.bind(exchange,
                         settings.USER_QUEUE.format(user_id=message.from_user.id)
                         )

        await user_queue.bind(exchange, 'user_messages')

        body = {
            'user_id': message.from_user.id,
            'action': 'login'
        }

        await exchange.publish(
            aio_pika.Message(msgpack.packb(body)),
            'user_messages'
        )