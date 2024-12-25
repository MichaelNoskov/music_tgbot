from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from src.handlers.command.router import router
from src.templates.env import render
from src.handlers.states.auth import AuthGroup


@router.message(Command('start'), AuthGroup.authorized)
async def menu(message: Message) -> None:
    inline_kb_list = [
        [InlineKeyboardButton(text='Слушать музыку', callback_data='get_music')],
        [InlineKeyboardButton(text='Слушать любимую музыку', callback_data='get_favorite_music')],
        [InlineKeyboardButton(text='Загрузить музыку', callback_data='upload_music')],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    await message.answer(render('menu.jinja2'), reply_markup=reply_markup)


@router.message(Command('start'))
async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(AuthGroup.no_authorized)
    await message.answer(render('start.jinja2'))
