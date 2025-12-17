"""Renders package."""
from .i18n import I18n, get_i18n
from .keyboard import (
    language_keyboard,
    home_keyboard,
    settings_keyboard,
    level_keyboard,
    question_keyboard,
    result_keyboard,
)
from .page import (
    HomePageRender,
    SettingsPageRender,
    LanguagePageRender,
    LevelListPageRender,
    QuestionPageRender,
    ResultPageRender,
)

__all__ = [
    "I18n",
    "get_i18n",
    "language_keyboard",
    "home_keyboard",
    "settings_keyboard",
    "level_keyboard",
    "question_keyboard",
    "result_keyboard",
    "HomePageRender",
    "SettingsPageRender",
    "LanguagePageRender",
    "LevelListPageRender",
    "QuestionPageRender",
    "ResultPageRender",
]
