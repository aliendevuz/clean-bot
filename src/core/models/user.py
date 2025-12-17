"""User model.

User - botdagi foydalanuvchi ma'lumotlarini saqlaydi.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Foydalanuvchi modeli."""
    id: int  # Telegram user_id
    name: str
    language: str  # 'uz', 'en', 'ru'
    created_at: Optional[datetime] = None

    @staticmethod
    def from_row(row: tuple) -> "User":
        """SQLite row dan User yaratish."""
        return User(
            id=row[0],
            name=row[1],
            language=row[2],
            created_at=datetime.fromisoformat(row[3]) if row[3] else None
        )
