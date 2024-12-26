from aiogram import F
import msgpack
from config.settings import settings
from aiogram.types import CallbackQuery
from src.storage.rabbit import channel_pool
import aio_pika
from aio_pika import ExchangeType
import asyncio

from src.handlers.callback.router import router
from src.templates.keyboards import get_like_keyboard
from src.metrics import track_latency, SEND_MESSAGE
from src.handlers.states.auth import AuthGroup


@router.callback_query(lambda query: 'like' in str(query.data), AuthGroup.authorized)
@track_latency('like-dislike')
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
        SEND_MESSAGE.inc()
        

        user_queue_name = settings.USER_QUEUE.format(user_id=call.from_user.id)
        user_queue = await channel.declare_queue(user_queue_name, durable=True)

        await user_queue.bind(exchange, user_queue_name)
    
        retries = 3
        info = {'liked': action != 'like'}
        for _ in range(retries):
            try:
                answer = await user_queue.get()
                info = msgpack.unpackb(answer.body)
            except asyncio.QueueEmpty:
                await asyncio.sleep(1)    

    reply_markup = get_like_keyboard(info.get('liked'), music_id)

    await call.message.bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=reply_markup
    )


    # await call.message.('Добавлено в понравившиеся\n(кнопка обновится при повторном открытии музыки)')