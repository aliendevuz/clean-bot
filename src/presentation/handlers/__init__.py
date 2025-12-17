"""Handlers package."""
from .commands import start_router
from .callbacks import language_router, navigation_router, quiz_router, statistics_router
from .messages import name_input_router

__all__ = [
    "start_router",
    "language_router",
    "navigation_router",
    "quiz_router",
    "statistics_router",
    "name_input_router",
]
