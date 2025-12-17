"""Language selection page render."""
from aiogram.types import InlineKeyboardMarkup

from src.presentation.renders.i18n import I18n
from src.presentation.renders.keyboard import language_keyboard


class LanguagePageRender:
    """Til tanlash sahifasi renderi."""

    def __init__(self, i18n: I18n):
        self.i18n = i18n

    def get_text(self) -> str:
        """Sahifa matnini olish."""
        return self.i18n.get("choose_language")

    def get_keyboard(self) -> InlineKeyboardMarkup:
        """Sahifa keyboardini olish."""
        return language_keyboard()
