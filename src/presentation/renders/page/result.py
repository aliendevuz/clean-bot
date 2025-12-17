"""Level result page render."""
from aiogram.types import InlineKeyboardMarkup

from src.presentation.renders.i18n import I18n
from src.presentation.renders.keyboard import result_keyboard


class ResultPageRender:
    """Natija sahifasi renderi."""

    def __init__(self, i18n: I18n, operation: str, level: int, 
                 correct: int, total: int):
        self.i18n = i18n
        self.operation = operation
        self.level = level
        self.correct = correct
        self.total = total

    def get_text(self) -> str:
        """Sahifa matnini olish."""
        percent = int((self.correct / self.total) * 100) if self.total > 0 else 0
        return self.i18n.get(
            "level_complete",
            correct=self.correct,
            total=self.total,
            percent=percent
        )

    def get_keyboard(self) -> InlineKeyboardMarkup:
        """Sahifa keyboardini olish."""
        return result_keyboard(self.i18n, self.operation, self.level)
