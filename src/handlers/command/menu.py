from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.handlers.command.router import router
from src.templates.env import render


@router.message(Command('menu'))
async def menu(message: Message) -> None:
    inline_kb_list = [
        [InlineKeyboardButton(text='Слушать музыку', callback_data='get_music')],
        [InlineKeyboardButton(text='Слушать любимую музыку', callback_data='get_favorite_music')],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    await message.answer(render('menu.jinja2'), reply_markup=reply_markup)