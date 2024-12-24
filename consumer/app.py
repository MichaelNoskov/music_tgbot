import logging.config

import msgpack

from consumer.handlers.event_distribution import handle_event_distribution
from consumer.logger import LOGGING_CONFIG, logger, correlation_id_ctx
from src.storage import rabbit


async def main() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info('Запуск consumer...')
    queue_name = 'user_ask'
    async with rabbit.channel_pool.acquire() as channel:

        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)

        logger.info('Consumer Запущен!')

        async with queue.iterator() as queue_iter:
            logger.info('<queue iterator>')
            async for message in queue_iter:
                async with message.process():

                    correlation_id_ctx.set(message.correlation_id)
                    body = msgpack.unpackb(message.body)

                    logger.info("Message: %s", body)
                    await handle_event_distribution(body)
