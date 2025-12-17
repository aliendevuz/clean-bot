"""Question page render."""
from aiogram.types import InlineKeyboardMarkup

from src.presentation.renders.i18n import I18n
from src.presentation.renders.keyboard import question_keyboard
from src.core.services.quiz_service import Question


class QuestionPageRender:
    """Savol sahifasi renderi."""

    def __init__(self, i18n: I18n, question: Question, current: int, total: int):
        self.i18n = i18n
        self.question = question
        self.current = current
        self.total = total

    def get_text(self) -> str:
        """Sahifa matnini olish."""
        header = self.i18n.get("question_header", current=self.current, total=self.total)
        question_text = self.i18n.get("quiz_question", question=self.question.text)
        return header + question_text

    def get_keyboard(self) -> InlineKeyboardMarkup:
        """Sahifa keyboardini olish."""
        return question_keyboard(self.question)
