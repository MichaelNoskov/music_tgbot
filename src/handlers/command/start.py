import aio_pika
from aiogram.filters import Command
from aiogram.types import Message

from src.handlers.command.router import router
from src.templates.env import render
from src.storage.rabbit import channel_pool
from config.settings import settings


@router.message(Command('start'))
async def menu(message: Message) -> None:
    await message.answer(render('start.jinja2'))
