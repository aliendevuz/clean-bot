"""Callbacks handlers package."""
from .language import router as language_router
from .navigation import router as navigation_router
from .quiz import router as quiz_router
from .statistics import router as statistics_router

__all__ = ["language_router", "navigation_router", "quiz_router", "statistics_router"]
