"""Progress repository implementation.

ProgressRepository interfaceni SQLite database bilan implement qiladi.
"""
from typing import Optional, List

from src.core.models import Progress
from src.core.repositories import ProgressRepository
from src.data.sqlite import ProgressDatabase


class ProgressRepositoryImpl(ProgressRepository):
    """SQLite-based progress repository implementation."""

    def __init__(self, database: ProgressDatabase):
        self.db = database

    async def save(self, progress: Progress) -> Progress:
        """Progress saqlash."""
        row = await self.db.insert(
            progress.user_id,
            progress.operation,
            progress.level,
            progress.correct_answers,
            progress.total_questions
        )
        return Progress.from_row(row)

    async def get_best_score(self, user_id: int, operation: str, level: int) -> Optional[Progress]:
        """User ning eng yaxshi natijasini olish."""
        row = await self.db.select_best_score(user_id, operation, level)
        if row:
            return Progress.from_row(row)
        return None

    async def get_user_progress(self, user_id: int, operation: str) -> List[Progress]:
        """User ning ma'lum operatsiya bo'yicha barcha progressini olish."""
        rows = await self.db.select_by_user_and_operation(user_id, operation)
        return [Progress.from_row(row) for row in rows]
