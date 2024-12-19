from aiogram import F
from aiogram.types import CallbackQuery, Message

from src.handlers.callback.router import router


@router.callback_query(F.data == 'get_favorite_music')
async def get_popular_recipe(call: CallbackQuery) -> None:
    if isinstance(call.message, Message):
        await call.answer('Выбираю трек, который вам нравится...')

    await call.message.answer('Попробуйте позже, мне ещё не подключили базу данных)))')