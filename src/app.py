from aiogram import Bot, Dispatcher
from src.config.env import BOT_TOKEN


async def run_bot():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(bot)
