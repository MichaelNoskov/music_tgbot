from aiogram import F
import aio_pika
import msgpack
from config.settings import settings
from aiogram.types import CallbackQuery, Message
from src.storage.rabbit import channel_pool
import asyncio
from src.templates.env import render

from src.handlers.callback.router import router


@router.callback_query(F.data == 'get_music')
async def get_popular_recipe(call: CallbackQuery) -> None:
    if isinstance(call.message, Message):
        await call.answer('Подбираю музыку для вас...')

    async with channel_pool.acquire() as channel:

        user_queue_name = settings.USER_QUEUE.format(user_id=call.from_user.id)
        user_queue = await channel.declare_queue(user_queue_name, durable=True)

        retries = 3
        for _ in range(retries):
            try:
                answer = await user_queue.get()
                info = msgpack.unpackb(answer.body)

                music_text = render('music.jinja2', recipe=info)

                await call.message.answer(music_text)
                return

            except asyncio.QueueEmpty:
                await asyncio.sleep(1)

        if isinstance(call.message, Message):
            await call.message.answer('Ошибка при получении популярных рецептов. Попробуйте позже.')


    await call.message.answer('Попробуйте позже, ме ещё не подключили базу данных)))')