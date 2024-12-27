import asyncio
from src.bot import bot, dp


async def tg_bot():
    await dp.start_polling(bot, handle_signals=False)


if __name__ == '__main__':
    asyncio.run(tg_bot())
