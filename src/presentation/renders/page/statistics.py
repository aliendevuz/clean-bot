"""Statistics page render."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.presentation.renders.i18n import I18n


class StatisticsPageRender:
    """Statistika sahifasi renderi."""

    def __init__(self, i18n: I18n, user_name: str, summary: dict):
        self.i18n = i18n
        self.user_name = user_name
        self.summary = summary

    def get_text(self) -> str:
        """Sahifa matnini olish."""
        if self.summary["total_games"] == 0:
            return self.i18n.get("statistics_no_data")
        
        text = self.i18n.get("statistics_title", name=self.user_name)
        text += self.i18n.get(
            "statistics_summary",
            total_games=self.summary["total_games"],
            correct=self.summary["correct"],
            total=self.summary["total"],
            percent=self.summary["percent"]
        )
        return text

    def get_keyboard(self) -> InlineKeyboardMarkup:
        """Sahifa keyboardini olish."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=self.i18n.get("back"), callback_data="page:home")]
        ])

    def get_chart_caption(self, days: int) -> str:
        """Grafik caption'ini olish."""
        return self.i18n.get("statistics_chart_caption", days=days)
