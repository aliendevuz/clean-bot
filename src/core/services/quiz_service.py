"""Quiz service.

Matematik savollar generatsiyasi va javoblarni tekshirish.
"""
import random
from dataclasses import dataclass
from typing import List, Optional

from src.core.models import Progress
from src.core.repositories import ProgressRepository


@dataclass
class Question:
    """Savol modeli."""
    text: str
    correct_answer: int
    options: List[int]  # 4 ta variant, to'g'ri javob ham ichida


@dataclass
class LevelConfig:
    """Level konfiguratsiyasi."""
    min_num: int
    max_num: int
    questions_count: int


# Level qoidalari
LEVEL_CONFIGS: dict[int, LevelConfig] = {
    1: LevelConfig(min_num=1, max_num=10, questions_count=5),
    2: LevelConfig(min_num=1, max_num=20, questions_count=5),
    3: LevelConfig(min_num=1, max_num=30, questions_count=6),
    4: LevelConfig(min_num=1, max_num=50, questions_count=6),
    5: LevelConfig(min_num=1, max_num=70, questions_count=7),
    6: LevelConfig(min_num=1, max_num=100, questions_count=7),
    7: LevelConfig(min_num=10, max_num=100, questions_count=8),
    8: LevelConfig(min_num=10, max_num=150, questions_count=8),
    9: LevelConfig(min_num=20, max_num=200, questions_count=9),
    10: LevelConfig(min_num=50, max_num=300, questions_count=10),
}

# Operatsiya turlari
OPERATIONS = ["addition", "subtraction", "multiplication", "division"]


class QuizService:
    """Quiz bilan ishlash uchun service."""

    def __init__(self, progress_repo: ProgressRepository):
        self.progress_repo = progress_repo

    def get_level_config(self, level: int) -> LevelConfig:
        """Level konfiguratsiyasini olish."""
        return LEVEL_CONFIGS.get(level, LEVEL_CONFIGS[1])

    def generate_question(self, operation: str, level: int) -> Question:
        """
        Savol generatsiya qilish.
        
        Args:
            operation: 'addition', 'subtraction', 'multiplication', 'division'
            level: 1-10
        """
        config = self.get_level_config(level)
        
        if operation == "addition":
            return self._generate_addition(config)
        elif operation == "subtraction":
            return self._generate_subtraction(config)
        elif operation == "multiplication":
            return self._generate_multiplication(config)
        elif operation == "division":
            return self._generate_division(config)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def _generate_addition(self, config: LevelConfig) -> Question:
        """Qo'shish savolini yaratish."""
        a = random.randint(config.min_num, config.max_num)
        b = random.randint(config.min_num, config.max_num)
        correct = a + b
        
        text = f"{a} + {b} = ?"
        options = self._generate_options(correct, config)
        return Question(text=text, correct_answer=correct, options=options)

    def _generate_subtraction(self, config: LevelConfig) -> Question:
        """Ayirish savolini yaratish (natija manfiy bo'lmasin)."""
        a = random.randint(config.min_num, config.max_num)
        b = random.randint(config.min_num, min(a, config.max_num))
        correct = a - b
        
        text = f"{a} - {b} = ?"
        options = self._generate_options(correct, config)
        return Question(text=text, correct_answer=correct, options=options)

    def _generate_multiplication(self, config: LevelConfig) -> Question:
        """Ko'paytirish savolini yaratish."""
        # Ko'paytirish uchun sonlar kichikroq
        max_mult = min(config.max_num // 5, 20)
        a = random.randint(1, max(2, max_mult))
        b = random.randint(1, max(2, max_mult))
        correct = a * b
        
        text = f"{a} × {b} = ?"
        options = self._generate_options(correct, config)
        return Question(text=text, correct_answer=correct, options=options)

    def _generate_division(self, config: LevelConfig) -> Question:
        """Bo'lish savolini yaratish (butun sonli natija)."""
        # Oldin javobni va bo'luvchini tanlaymiz
        max_div = min(config.max_num // 5, 15)
        b = random.randint(1, max(2, max_div))
        correct = random.randint(1, max(2, max_div))
        a = b * correct  # Bo'linuvchi
        
        text = f"{a} ÷ {b} = ?"
        options = self._generate_options(correct, config)
        return Question(text=text, correct_answer=correct, options=options)

    def _generate_options(self, correct: int, config: LevelConfig) -> List[int]:
        """4 ta variant generatsiya qilish."""
        options = {correct}
        
        # Yaqin sonlardan noto'g'ri variantlar
        attempts = 0
        while len(options) < 4 and attempts < 20:
            # Yaqin oraliqda variant
            delta = random.randint(1, max(5, correct // 3 + 1))
            wrong = correct + random.choice([-1, 1]) * delta
            if wrong >= 0 and wrong != correct:
                options.add(wrong)
            attempts += 1
        
        # Agar yetarli variant bo'lmasa
        while len(options) < 4:
            wrong = random.randint(0, config.max_num * 2)
            if wrong != correct:
                options.add(wrong)
        
        # Aralashtirish
        options_list = list(options)
        random.shuffle(options_list)
        return options_list

    def check_answer(self, question: Question, user_answer: int) -> bool:
        """Javobni tekshirish."""
        return question.correct_answer == user_answer

    async def save_progress(self, user_id: int, operation: str, level: int,
                           correct_answers: int, total_questions: int) -> Progress:
        """Progress saqlash."""
        progress = Progress(
            id=None,
            user_id=user_id,
            operation=operation,
            level=level,
            correct_answers=correct_answers,
            total_questions=total_questions
        )
        return await self.progress_repo.save(progress)

    async def get_best_score(self, user_id: int, operation: str, level: int) -> Optional[Progress]:
        """Eng yaxshi natijani olish."""
        return await self.progress_repo.get_best_score(user_id, operation, level)

    def get_questions_count(self, level: int) -> int:
        """Level uchun savollar sonini olish."""
        config = self.get_level_config(level)
        return config.questions_count

    async def get_user_statistics(self, user_id: int, days: int = 30) -> List[Progress]:
        """User ning oxirgi N kunlik natijalarini olish."""
        return await self.progress_repo.get_user_statistics(user_id, days)

    async def get_user_total_stats(self, user_id: int) -> dict:
        """User ning umumiy statistikasini olish."""
        return await self.progress_repo.get_user_total_stats(user_id)
