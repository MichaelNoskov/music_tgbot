import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from config.settings import settings
from src.logger import set_correlation_id
from src.api.router import router
from src.bot import bot, dp
from src.logger import logger
from src.metrics import RPSTrackerMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    polling_task: asyncio.Task[None] | None = None
    wh_info = await bot.get_webhook_info()
    if settings.BOT_WEBHOOK_URL and wh_info != settings.BOT_WEBHOOK_URL:
        logger.info('Webhook in use')
        await bot.set_webhook(settings.BOT_WEBHOOK_URL)
    else:
        polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
        logger.info('Start polling')

    yield

    if polling_task is not None:
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            logger.info('Stop polling')

    await bot.delete_webhook()


def create_app() -> FastAPI:

    cor_id = set_correlation_id()
    app = FastAPI(docs_url='/swagger', lifespan=lifespan)
    app.include_router(router)
    app.add_middleware(RPSTrackerMiddleware)
    logger.info(f'Successful started... {cor_id}')
    return app
