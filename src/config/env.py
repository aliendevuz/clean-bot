from dotenv import load_dotenv
from os import getenv


load_dotenv()

# Load env
BOT_TOKEN = getenv("BOT_TOKEN")
ADMINS = getenv("ADMINS").split(',')
DATABASE_URL = getenv("DATABASE_URL")

# Validate env
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN is not exist")

if len(ADMINS) < 1:
    raise Exception("ADMINS is empty")

if not DATABASE_URL:
    raise Exception("DATABASE_URL is not exist")
