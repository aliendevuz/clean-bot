"""Entry point.

Botni ishga tushirish uchun main fayl.
"""
import asyncio
import logging
from src.app import run_bot

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    asyncio.run(run_bot())
