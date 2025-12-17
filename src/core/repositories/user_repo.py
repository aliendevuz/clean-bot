"""User repository interface.

Bu interface user ma'lumotlari bilan ishlash uchun kerakli metodlarni belgilaydi.
Har bir database uchun alohida implementation bo'ladi.
"""
from abc import ABC, abstractmethod
from typing import Optional

from src.core.models import User


class UserRepository(ABC):
    """User repository abstract class."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Yangi user yaratish."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """User ID bo'yicha olish."""
        pass

    @abstractmethod
    async def update_language(self, user_id: int, language: str) -> bool:
        """User tilini yangilash."""
        pass

    @abstractmethod
    async def update_name(self, user_id: int, name: str) -> bool:
        """User ismini yangilash."""
        pass

    @abstractmethod
    async def exists(self, user_id: int) -> bool:
        """User mavjudligini tekshirish."""
        pass
