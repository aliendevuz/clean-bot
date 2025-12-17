"""Settings page render."""
from aiogram.types import InlineKeyboardMarkup

from src.presentation.renders.i18n import I18n
from src.presentation.renders.keyboard import settings_keyboard


class SettingsPageRender:
    """Sozlamalar sahifasi renderi."""

    def __init__(self, i18n: I18n):
        self.i18n = i18n

    def get_text(self) -> str:
        """Sahifa matnini olish."""
        return self.i18n.get("settings_menu")

    def get_keyboard(self) -> InlineKeyboardMarkup:
        """Sahifa keyboardini olish."""
        return settings_keyboard(self.i18n)
