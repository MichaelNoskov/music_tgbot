from aiogram import F
from aiogram.types import CallbackQuery, Message
from src.storage.rabbit import channel_pool
import aio_pika
from aio_pika import ExchangeType
import asyncio
import msgpack
from config.settings import settings
from aiogram.types import BufferedInputFile

from src.templates.keyboards import get_like_keyboard
from src.storage.minio_ import get_music as get_music_from_minio
from src.handlers.callback.router import router
from src.templates.env import render


@router.callback_query(F.data == 'get_favorite_music')
async def get_favorite_music(call: CallbackQuery) -> None:
    if isinstance(call.message, Message):
        await call.answer('Ищу ваши любимые треки...')
    
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange('user_music', ExchangeType.DIRECT, durable=True)
    
        queue = await channel.declare_queue('user_ask', durable=True)
        await queue.bind(exchange, 'user_ask')

        body = {'user_id': call.from_user.id, 'action': 'get_favorite_music'}
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
                
                music_objs = info.get('music')

                if len(music_objs) < 1:
                    await call.message.answer('У вас нет понравившейся музыки')
                    return


                await call.message.answer('Ваша любимая музыка:')
                for music in music_objs:
                    music_text = render('music.jinja2', music=music)

                    audio_bytes = await get_music_from_minio(music.get('file_url'))

                    reply_markup = get_like_keyboard(music.get('liked'), music.get("music_id"))

                    await call.message.answer_audio(
                        BufferedInputFile(audio_bytes, 'music.mp3'),
                        caption=music_text,
                        reply_markup=reply_markup,
                    )
                await call.message.answer('👆 Музыка загружена 👆\n/start - показать меню')        
                return

            except asyncio.QueueEmpty:
                await asyncio.sleep(1)

        await call.message.answer('Попробуйте позже, ме ещё не подключили базу данных)))')
