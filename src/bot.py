from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from config.settings import settings
from src.handlers.callback.router import router as callback_router
from src.handlers.command.router import router as command_router
from src.handlers.auth.router import router as auth_router
from src.handlers.upload_music.router import router as music_router
from src.storage.redis import redis_storage

default = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=settings.BOT_TOKEN, default=default)
dp = Dispatcher(storage=RedisStorage(redis=redis_storage))

dp.include_router(command_router)
dp.include_router(auth_router)
dp.include_router(music_router)
dp.include_router(callback_router)
