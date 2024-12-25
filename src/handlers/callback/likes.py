from aiogram import F
import msgpack
from config.settings import settings
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from src.storage.rabbit import channel_pool
import asyncio
from src.templates.env import render
import aio_pika
from aio_pika import ExchangeType
from io import BytesIO
from src.storage.minio_ import get_music as get_music_from_minio
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.handlers.callback.router import router


@router.callback_query(lambda query: 'like' in str(query.data))
async def likes(call: CallbackQuery) -> None:
    
    action, music_id = call.data.split(':')

    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange('user_music', ExchangeType.DIRECT, durable=True)
    
        queue = await channel.declare_queue('user_ask', durable=True)
        await queue.bind(exchange, 'user_ask')

        body = {'user_id': call.from_user.id, 'action': action, 'music_id': music_id}
        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(
                    body
                ),
            ),
            'user_ask'
        )

        await call.message.answer('Добавлено в понравившиеся\n(кнопка обновится при повторном открытии музыки)')