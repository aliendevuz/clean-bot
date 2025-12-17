"""Page renders package."""
from .home import HomePageRender
from .settings import SettingsPageRender
from .language import LanguagePageRender
from .level_list import LevelListPageRender
from .question import QuestionPageRender
from .result import ResultPageRender
from .statistics import StatisticsPageRender

__all__ = [
    "HomePageRender",
    "SettingsPageRender",
    "LanguagePageRender",
    "LevelListPageRender",
    "QuestionPageRender",
    "ResultPageRender",
    "StatisticsPageRender",
]
