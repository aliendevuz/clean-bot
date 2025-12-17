"""Inline keyboard renders.

Barcha inline keyboardlarni yaratuvchi modullar.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from src.presentation.renders.i18n import I18n
from src.core.services.quiz_service import Question


def language_keyboard() -> InlineKeyboardMarkup:
    """Til tanlash keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
    ])


def home_keyboard(i18n: I18n) -> InlineKeyboardMarkup:
    """Bosh sahifa keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=i18n.get("addition"), callback_data="op:addition"),
            InlineKeyboardButton(text=i18n.get("subtraction"), callback_data="op:subtraction"),
        ],
        [
            InlineKeyboardButton(text=i18n.get("multiplication"), callback_data="op:multiplication"),
            InlineKeyboardButton(text=i18n.get("division"), callback_data="op:division"),
        ],
        [
            InlineKeyboardButton(text=i18n.get("settings"), callback_data="page:settings"),
        ],
    ])


def settings_keyboard(i18n: I18n) -> InlineKeyboardMarkup:
    """Sozlamalar keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.get("change_name"), callback_data="action:change_name")],
        [InlineKeyboardButton(text=i18n.get("change_language"), callback_data="action:change_language")],
        [InlineKeyboardButton(text=i18n.get("back"), callback_data="page:home")],
    ])


def level_keyboard(i18n: I18n, operation: str) -> InlineKeyboardMarkup:
    """Level tanlash keyboard."""
    buttons: List[List[InlineKeyboardButton]] = []
    
    # 2 qatorga 5 tadan level
    for row_start in range(1, 11, 5):
        row = []
        for level in range(row_start, min(row_start + 5, 11)):
            row.append(InlineKeyboardButton(
                text=f"{level}",
                callback_data=f"level:{operation}:{level}"
            ))
        buttons.append(row)
    
    # Orqaga tugmasi
    buttons.append([InlineKeyboardButton(text=i18n.get("back"), callback_data="page:home")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def question_keyboard(question: Question) -> InlineKeyboardMarkup:
    """Savol javob variantlari keyboard."""
    buttons: List[List[InlineKeyboardButton]] = []
    
    # 2 qatorga 2 tadan variant
    for i in range(0, len(question.options), 2):
        row = []
        for j in range(i, min(i + 2, len(question.options))):
            option = question.options[j]
            row.append(InlineKeyboardButton(
                text=str(option),
                callback_data=f"answer:{option}"
            ))
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def result_keyboard(i18n: I18n, operation: str, level: int) -> InlineKeyboardMarkup:
    """Natija sahifasi keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=i18n.get("retry_level"),
            callback_data=f"level:{operation}:{level}"
        )],
        [InlineKeyboardButton(
            text=i18n.get("choose_another_level"),
            callback_data=f"op:{operation}"
        )],
        [InlineKeyboardButton(
            text=i18n.get("home_button"),
            callback_data="page:home"
        )],
    ])
