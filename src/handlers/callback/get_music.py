from aiogram import F
import msgpack
from config.settings import settings
from aiogram.types import CallbackQuery, Message
from src.storage.rabbit import channel_pool
import asyncio
from src.templates.env import render
import aio_pika
from aio_pika import ExchangeType

from src.handlers.callback.router import router


@router.callback_query(F.data == 'get_music')
async def get_music(call: CallbackQuery) -> None:
    if isinstance(call.message, Message):
        await call.answer('Подбираю музыку для вас...')

    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange('user_music', ExchangeType.DIRECT, durable=True)
    
        queue = await channel.declare_queue('user_ask', durable=True)
        await queue.bind(exchange, 'user_ask')

        body = {'user_id': call.from_user.id, 'action': 'get_music'}
        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(
                    body
                ),
            ),
            'user_ask'
        )

        user_queue_name = settings.USER_QUEUE.format(user_id=call.from_user.id)
        user_queue = await channel.declare_queue(user_queue_name, durable=True)

        await user_queue.bind(exchange, user_queue_name)
    
        retries = 3
        for _ in range(retries):
            try:
                answer = await user_queue.get()
                info = msgpack.unpackb(answer.body)        

                music_text = render('music.jinja2', music=info)

                await call.message.answer(music_text)
                return

            except asyncio.QueueEmpty:
                await asyncio.sleep(1)

        await call.message.answer('Попробуйте позже, ме ещё не подключили базу данных)))')