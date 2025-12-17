"""Internationalization (i18n) module.

Tarjimalarni boshqaruvchi modul.
"""
from typing import Any

from .uz import UZ
from .en import EN
from .ru import RU


TRANSLATIONS = {
    "uz": UZ,
    "en": EN,
    "ru": RU,
}


class I18n:
    """Tarjimalar bilan ishlash uchun class."""

    def __init__(self, language: str = "uz"):
        self.language = language

    def get(self, key: str, **kwargs: Any) -> str:
        """
        Tarjimani olish.
        
        Args:
            key: Tarjima kaliti
            **kwargs: Format parametrlari
            
        Returns:
            Tarjima matni
        """
        translations = TRANSLATIONS.get(self.language, UZ)
        text = translations.get(key, key)
        
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        
        return text

    def set_language(self, language: str):
        """Tilni o'zgartirish."""
        if language in TRANSLATIONS:
            self.language = language

    @staticmethod
    def get_available_languages() -> list[str]:
        """Mavjud tillar ro'yxatini olish."""
        return list(TRANSLATIONS.keys())


def get_i18n(language: str = "uz") -> I18n:
    """I18n instance yaratish."""
    return I18n(language)
