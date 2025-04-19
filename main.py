import os
import asyncio
from aiogram import types
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from models import create_tables
from hendlers.ls.player  import player_router
from hendlers.ls.info import player_router
from hendlers.ls.penalty_ls import player_router
from hendlers.ls.treasure_ls import player_router
from hendlers.ls.KMN_ls import player_router
from hendlers.ls.profile import player_router
from hendlers.ls.ochko_ls import player_router
from hendlers.ls.magaz import player_router
from hendlers.group.ochko import ochko_router
from hendlers.ls.ranks import player_router
from hendlers.group.KMN import KMN_router
from hendlers.group.penalty import penalty_router
from hendlers.group.stakanchiki import stakan_router
from hendlers.ls.tournament_manager import manager_router, player_router


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Подключаем router
dp.include_router(player_router)
dp.include_router(KMN_router)
dp.include_router(penalty_router)
dp.include_router(stakan_router)
dp.include_router(ochko_router)
dp.include_router(manager_router)

async def main():
    
    await create_tables()
    print("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

