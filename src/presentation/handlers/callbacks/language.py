"""Language selection callback handler.

Til tanlash callback'larini qayta ishlash.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.core.models import User
from src.presentation.renders import HomePageRender, get_i18n

router = Router(name="language")


@router.callback_query(F.data.startswith("lang:"))
async def on_language_select(callback: CallbackQuery, user_service, state_manager, user_exists: bool):
    """
    Til tanlash callback handleri.
    
    callback_data format: "lang:uz" | "lang:en" | "lang:ru"
    """
    language = callback.data.split(":")[1]
    user_id = callback.from_user.id
    user_id_str = str(user_id)
    
    if not user_exists:
        # Yangi user yaratish
        name = callback.from_user.full_name or "User"
        user = User(id=user_id, name=name, language=language)
        await user_service.user_repo.create(user)
    else:
        # Tilni yangilash
        await user_service.update_language(user_id, language)
    
    # Bosh sahifaga o'tish
    i18n = get_i18n(language)
    render = HomePageRender(i18n)
    
    await callback.message.edit_text(
        text=render.get_text(),
        reply_markup=render.get_keyboard()
    )
    
    # Navigation yangilash
    user_state = state_manager.get_user_state(user_id_str)
    if user_state:
        user_state.navigation.reset("HOME")
    
    await callback.answer(i18n.get("language_changed"))
