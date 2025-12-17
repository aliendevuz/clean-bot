"""Progress repository interface.

Bu interface user progress ma'lumotlari bilan ishlash uchun kerakli metodlarni belgilaydi.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from src.core.models import Progress


class ProgressRepository(ABC):
    """Progress repository abstract class."""

    @abstractmethod
    async def save(self, progress: Progress) -> Progress:
        """Progress saqlash."""
        pass

    @abstractmethod
    async def get_best_score(self, user_id: int, operation: str, level: int) -> Optional[Progress]:
        """User ning eng yaxshi natijasini olish."""
        pass

    @abstractmethod
    async def get_user_progress(self, user_id: int, operation: str) -> List[Progress]:
        """User ning ma'lum operatsiya bo'yicha barcha progressini olish."""
        pass
