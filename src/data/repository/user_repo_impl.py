"""User repository implementation.

UserRepository interfaceni SQLite database bilan implement qiladi.
"""
from typing import Optional

from src.core.models import User
from src.core.repositories import UserRepository
from src.data.sqlite import UserDatabase


class UserRepositoryImpl(UserRepository):
    """SQLite-based user repository implementation."""

    def __init__(self, database: UserDatabase):
        self.db = database

    async def create(self, user: User) -> User:
        """Yangi user yaratish."""
        row = await self.db.insert(user.id, user.name, user.language)
        return User.from_row(row)

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """User ID bo'yicha olish."""
        row = await self.db.select_by_id(user_id)
        if row:
            return User.from_row(row)
        return None

    async def update_language(self, user_id: int, language: str) -> bool:
        """User tilini yangilash."""
        return await self.db.update_language(user_id, language)

    async def update_name(self, user_id: int, name: str) -> bool:
        """User ismini yangilash."""
        return await self.db.update_name(user_id, name)

    async def exists(self, user_id: int) -> bool:
        """User mavjudligini tekshirish."""
        return await self.db.exists(user_id)
