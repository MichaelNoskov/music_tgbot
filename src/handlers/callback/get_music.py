from aiogram import F
from aiogram.types import CallbackQuery, Message

from src.handlers.callback.router import router


@router.callback_query(F.data == 'get_music')
async def get_popular_recipe(call: CallbackQuery) -> None:
    if isinstance(call.message, Message):
        await call.answer('Подбираю музыку для вас...')

    await call.message.answer('Попробуйте позже, ме ещё не подключили базу данных)))')