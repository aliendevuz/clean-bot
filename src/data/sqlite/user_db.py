"""SQLite database module for users.

Raw SQL bilan user ma'lumotlarini boshqarish.
"""
import aiosqlite
from typing import Optional


class UserDatabase:
    """SQLite user database operations."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None

    async def init(self):
        """Database ulanishini ochish va jadval yaratish."""
        self.connection = await aiosqlite.connect(self.db_path)
        await self._create_table()

    async def close(self):
        """Database ulanishini yopish."""
        if self.connection:
            await self.connection.close()
            self.connection = None

    async def _create_table(self):
        """Users jadvalini yaratish."""
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                language TEXT NOT NULL DEFAULT 'uz',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self.connection.commit()

    async def insert(self, user_id: int, name: str, language: str) -> tuple:
        """Yangi user qo'shish."""
        cursor = await self.connection.execute(
            "INSERT INTO users (id, name, language) VALUES (?, ?, ?)",
            (user_id, name, language)
        )
        await self.connection.commit()
        
        # Yaratilgan userni qaytarish
        cursor = await self.connection.execute(
            "SELECT id, name, language, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        return await cursor.fetchone()

    async def select_by_id(self, user_id: int) -> Optional[tuple]:
        """User ID bo'yicha qidirish."""
        cursor = await self.connection.execute(
            "SELECT id, name, language, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        return await cursor.fetchone()

    async def update_language(self, user_id: int, language: str) -> bool:
        """User tilini yangilash."""
        cursor = await self.connection.execute(
            "UPDATE users SET language = ? WHERE id = ?",
            (language, user_id)
        )
        await self.connection.commit()
        return cursor.rowcount > 0

    async def update_name(self, user_id: int, name: str) -> bool:
        """User ismini yangilash."""
        cursor = await self.connection.execute(
            "UPDATE users SET name = ? WHERE id = ?",
            (name, user_id)
        )
        await self.connection.commit()
        return cursor.rowcount > 0

    async def exists(self, user_id: int) -> bool:
        """User mavjudligini tekshirish."""
        cursor = await self.connection.execute(
            "SELECT 1 FROM users WHERE id = ?",
            (user_id,)
        )
        return await cursor.fetchone() is not None
