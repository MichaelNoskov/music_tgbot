from aiogram.filters import Command
from aiogram.types import Message

from src.handlers.command.router import router
from src.templates.env import render


@router.message(Command('start'))
async def menu(message: Message) -> None:
    await message.answer(render('start.jinja2'))