import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import main_handler
import led

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_routers(main_handler.router)

async def start_bot():
    asyncio.ensure_future(led.timer())

async def st():
    dp.startup.register(start_bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(st())
    except Exception as e:
        print(e)