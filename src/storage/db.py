from uuid import uuid4

from asyncpg import Connection
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from typing_extensions import AsyncGenerator

from config.settings import settings
from src.logger import logger


class CConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f'__asyncpg_{prefix}_{uuid4()}__'


def create_engine() -> AsyncEngine:
    logger.info('Creating db engine')
    return create_async_engine(
        settings.db_url,
        poolclass=NullPool,
        connect_args={
            'connection_class': CConnection,
        },
    )


def create_session(_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    logger.info('Creating db session')
    return async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


engine = create_engine()
async_session = create_session(engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    logger.debug('Getting db session')
    async with async_session() as db:
        yield db
    logger.info('Db session was closed')
