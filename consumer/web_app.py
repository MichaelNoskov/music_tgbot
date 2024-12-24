import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from consumer.api.router import router as tech_router
from consumer.app import main
from consumer.logger import logger, logging, LOGGING_CONFIG


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:

    logging.config.dictConfig(LOGGING_CONFIG)

    logger.info('Starting lifespan')
    task = asyncio.create_task(main())

    logger.info('Started succesfully')
    yield

    if task is not None:
        logger.info("Stopping polling...")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info("Polling stopped")

    logger.info('Ending lifespan')


def create_app() -> FastAPI:
    app = FastAPI(docs_url='/swagger', lifespan=lifespan)
    app.include_router(tech_router, prefix='', tags=['tech'])
    return app
