"""Main application module.

Barcha qismlarni birlashtiruvchi va botni ishga tushiruvchi modul.
"""
import os
from typing import Any, Awaitable, Callable, Dict

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from src.config.env import BOT_TOKEN, DATABASE_URL
from core.state_manager import StateManager
from src.data.sqlite import UserDatabase, ProgressDatabase
from src.data.repository import UserRepositoryImpl, ProgressRepositoryImpl
from src.core.services import UserService, QuizService
from src.presentation.handlers import (
    start_router,
    language_router,
    navigation_router,
    quiz_router,
    name_input_router,
)


class DependencyMiddleware(BaseMiddleware):
    """
    Middleware barcha handlerlarga dependencylarni inject qilish uchun.
    
    Bu middleware har bir update kelganda:
    1. User mavjudligini tekshiradi
    2. User tilini oladi
    3. Kerakli service va managerlarni data ga qo'shadi
    """

    def __init__(
        self,
        user_service: UserService,
        quiz_service: QuizService,
        state_manager: StateManager,
    ):
        self.user_service = user_service
        self.quiz_service = quiz_service
        self.state_manager = state_manager

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # User ID olish
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id
        
        # User ma'lumotlarini olish
        user_exists = False
        user_language = "uz"
        
        if user_id:
            user = await self.user_service.get_user(user_id)
            if user:
                user_exists = True
                user_language = user.language
        
        # Data ga qo'shish
        data["user_service"] = self.user_service
        data["quiz_service"] = self.quiz_service
        data["state_manager"] = self.state_manager
        data["user_exists"] = user_exists
        data["user_language"] = user_language
        
        return await handler(event, data)


async def run_bot():
    """Botni ishga tushirish."""
    # Data papkasini yaratish
    os.makedirs("data", exist_ok=True)
    
    # Database'larni ishga tushirish
    user_db = UserDatabase(DATABASE_URL)
    progress_db = ProgressDatabase(DATABASE_URL)
    
    await user_db.init()
    await progress_db.init()
    
    # Repository'larni yaratish
    user_repo = UserRepositoryImpl(user_db)
    progress_repo = ProgressRepositoryImpl(progress_db)
    
    # Service'larni yaratish
    user_service = UserService(user_repo)
    quiz_service = QuizService(progress_repo)
    
    # State manager yaratish
    state_manager = StateManager()
    
    # Bot va Dispatcher yaratish
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Middleware qo'shish
    middleware = DependencyMiddleware(user_service, quiz_service, state_manager)
    dp.message.middleware(middleware)
    dp.callback_query.middleware(middleware)
    
    # Router'larni qo'shish
    dp.include_router(start_router)
    dp.include_router(language_router)
    dp.include_router(navigation_router)
    dp.include_router(quiz_router)
    dp.include_router(name_input_router)
    
    # Botni ishga tushirish
    print("🤖 Bot ishga tushdi...")
    try:
        await dp.start_polling(bot)
    finally:
        await user_db.close()
        await progress_db.close()
        await bot.session.close()

