import aio_pika
import msgpack

from aio_pika import ExchangeType
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.schema.music import MusicMessage
from src.handlers.states.auth import AuthGroup
from src.handlers.command.router import router
from src.templates.env import render
from src.storage.rabbit import channel_pool
from config.settings import settings


@router.message(Command('start'))
async def start(message: Message, state: FSMContext) -> None:
    async with channel_pool.acquire() as channel:   # type: aio_pika.Channel
        exchange = await channel.declare_exchange("user_music", ExchangeType.TOPIC, durable=True)

        queue = await channel.declare_queue(
            settings.USER_QUEUE.format(
                user_id=message.from_user.id,
            ),
            durable=True,
        )

        users_queue = await channel.declare_queue(
            'user_ask',
            durable=True,
        )

        await queue.bind(
            exchange,
            settings.USER_QUEUE.format(
                user_id=message.from_user.id,
            ),
        )
        await users_queue.bind(
            exchange,
            'user_ask'
        )

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(
                    MusicMessage(
                        user_id=message.from_user.id,
                        action='get_music',
                        event='gift'
                    )
                ),
            ),
            'user_ask'
        )
    
    await message.answer(render('start.jinja2'))
