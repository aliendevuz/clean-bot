"""SQLite database module for progress.

Raw SQL bilan progress ma'lumotlarini boshqarish.
"""
import aiosqlite
from typing import Optional, List


class ProgressDatabase:
    """SQLite progress database operations."""

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
        """Progress jadvalini yaratish."""
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                operation TEXT NOT NULL,
                level INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        await self.connection.commit()

    async def insert(self, user_id: int, operation: str, level: int, 
                     correct_answers: int, total_questions: int) -> tuple:
        """Yangi progress qo'shish."""
        cursor = await self.connection.execute(
            """INSERT INTO progress (user_id, operation, level, correct_answers, total_questions)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, operation, level, correct_answers, total_questions)
        )
        await self.connection.commit()
        
        # Yaratilgan progressni qaytarish
        cursor = await self.connection.execute(
            """SELECT id, user_id, operation, level, correct_answers, total_questions, completed_at
               FROM progress WHERE id = ?""",
            (cursor.lastrowid,)
        )
        return await cursor.fetchone()

    async def select_best_score(self, user_id: int, operation: str, level: int) -> Optional[tuple]:
        """Eng yaxshi natijani olish."""
        cursor = await self.connection.execute(
            """SELECT id, user_id, operation, level, correct_answers, total_questions, completed_at
               FROM progress 
               WHERE user_id = ? AND operation = ? AND level = ?
               ORDER BY correct_answers DESC, completed_at DESC
               LIMIT 1""",
            (user_id, operation, level)
        )
        return await cursor.fetchone()

    async def select_by_user_and_operation(self, user_id: int, operation: str) -> List[tuple]:
        """User ning ma'lum operatsiya bo'yicha barcha progressini olish."""
        cursor = await self.connection.execute(
            """SELECT id, user_id, operation, level, correct_answers, total_questions, completed_at
               FROM progress
               WHERE user_id = ? AND operation = ?
               ORDER BY level, completed_at DESC""",
            (user_id, operation)
        )
        return await cursor.fetchall()

    async def select_user_statistics(self, user_id: int, days: int = 30) -> List[tuple]:
        """User ning oxirgi N kunlik natijalarini olish."""
        cursor = await self.connection.execute(
            """SELECT id, user_id, operation, level, correct_answers, total_questions, completed_at
               FROM progress
               WHERE user_id = ? AND completed_at >= datetime('now', ?)
               ORDER BY completed_at ASC""",
            (user_id, f'-{days} days')
        )
        return await cursor.fetchall()

    async def select_user_total_stats(self, user_id: int) -> dict:
        """User ning umumiy statistikasini olish."""
        cursor = await self.connection.execute(
            """SELECT 
                   COUNT(*) as total_games,
                   COALESCE(SUM(correct_answers), 0) as total_correct,
                   COALESCE(SUM(total_questions), 0) as total_questions
               FROM progress
               WHERE user_id = ?""",
            (user_id,)
        )
        row = await cursor.fetchone()
        return {
            "total_games": row[0],
            "total_correct": row[1],
            "total_questions": row[2]
        }
