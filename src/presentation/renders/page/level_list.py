"""Level list page render."""
from aiogram.types import InlineKeyboardMarkup

from src.presentation.renders.i18n import I18n
from src.presentation.renders.keyboard import level_keyboard


class LevelListPageRender:
    """Level ro'yxati sahifasi renderi."""

    def __init__(self, i18n: I18n, operation: str):
        self.i18n = i18n
        self.operation = operation

    def get_text(self) -> str:
        """Sahifa matnini olish."""
        op_name = self.i18n.get(self.operation)
        return self.i18n.get("choose_level", operation=op_name)

    def get_keyboard(self) -> InlineKeyboardMarkup:
        """Sahifa keyboardini olish."""
        return level_keyboard(self.i18n, self.operation)
