"""Progress model.

Progress - foydalanuvchining har bir operatsiya va leveldagi natijalarini saqlaydi.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Progress:
    """Foydalanuvchi progress modeli."""
    id: Optional[int]
    user_id: int
    operation: str  # 'addition', 'subtraction', 'multiplication', 'division'
    level: int  # 1-10
    correct_answers: int
    total_questions: int
    completed_at: Optional[datetime] = None

    @staticmethod
    def from_row(row: tuple) -> "Progress":
        """SQLite row dan Progress yaratish."""
        return Progress(
            id=row[0],
            user_id=row[1],
            operation=row[2],
            level=row[3],
            correct_answers=row[4],
            total_questions=row[5],
            completed_at=datetime.fromisoformat(row[6]) if row[6] else None
        )
