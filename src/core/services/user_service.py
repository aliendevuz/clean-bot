"""User service.

User bilan bog'liq barcha biznes logikalarni boshqaradi.
"""
from typing import Optional

from src.core.models import User
from src.core.repositories import UserRepository


class UserService:
    """User bilan ishlash uchun service."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_or_create_user(self, user_id: int, name: str, default_language: str = "uz") -> tuple[User, bool]:
        """
        User olish yoki yangi yaratish.
        
        Returns:
            tuple[User, bool]: (User, is_new) - User va yangi yaratilganmi
        """
        existing = await self.user_repo.get_by_id(user_id)
        if existing:
            return existing, False
        
        new_user = User(id=user_id, name=name, language=default_language)
        created = await self.user_repo.create(new_user)
        return created, True

    async def get_user(self, user_id: int) -> Optional[User]:
        """User olish."""
        return await self.user_repo.get_by_id(user_id)

    async def update_language(self, user_id: int, language: str) -> bool:
        """User tilini yangilash."""
        return await self.user_repo.update_language(user_id, language)

    async def update_name(self, user_id: int, name: str) -> bool:
        """User ismini yangilash."""
        return await self.user_repo.update_name(user_id, name)

    async def user_exists(self, user_id: int) -> bool:
        """User mavjudligini tekshirish."""
        return await self.user_repo.exists(user_id)
