"""Environment configuration module.

.env fayldan barcha kerakli konfiguratsiyalarni yuklaydi va validatsiya qiladi.
"""
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Load env variables
BOT_TOKEN = getenv("BOT_TOKEN")
DATABASE_URL = getenv("DATABASE_URL", "data/bot.db")

# Validate required env variables
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN is not set in .env file")
