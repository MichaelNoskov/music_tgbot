from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from src.handlers.command.router import router
from src.templates.env import render
from src.handlers.states.auth import AuthGroup

from aio_pika import ExchangeType
import aio_pika
import msgpack
import asyncio
from config.settings import settings
from src.storage.rabbit import channel_pool
from src.metrics import track_latency, SEND_MESSAGE


@router.message(Command('start'), AuthGroup.authorized)
@track_latency('start')
async def menu(message: Message) -> None:
    inline_kb_list = [
        [InlineKeyboardButton(text='Слушать музыку', callback_data='get_music')],
        [InlineKeyboardButton(text='Слушать любимую музыку', callback_data='get_favorite_music')],
        [InlineKeyboardButton(text='Загрузить музыку', callback_data='upload_music')],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    await message.answer(render('menu.jinja2'), reply_markup=reply_markup)


@router.message(Command('start'))
@track_latency('start')
async def start(message: Message, state: FSMContext) -> None:

    # запрос в rabbit для сохранения данных в бд
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange('user_music', ExchangeType.DIRECT, durable=True)

        queue = await channel.declare_queue('user_ask', durable=True)
        await queue.bind(exchange, 'user_ask')

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb({'user_id': message.from_user.id, 'action': 'create_profile'}),
            ),
            'user_ask',
        )
        SEND_MESSAGE.inc()

        user_queue_name = settings.USER_QUEUE.format(user_id=message.from_user.id)
        user_queue = await channel.declare_queue(user_queue_name, durable=True)

        await user_queue.bind(exchange, user_queue_name)

        retries = 3

        info = {'authorized': False}

        for _ in range(retries):
            try:
                answer = await user_queue.get()
                info = msgpack.unpackb(answer.body)
            except asyncio.QueueEmpty:
                await asyncio.sleep(1)

        if info.get('authorized'):
            await state.set_state(AuthGroup.authorized)
            await menu(message)
            return

    await state.set_state(AuthGroup.no_authorized)
    await message.answer(render('start.jinja2'))
