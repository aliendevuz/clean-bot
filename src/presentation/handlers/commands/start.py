"""Start command handler.

/start buyrug'ini qayta ishlash.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.presentation.renders import LanguagePageRender, HomePageRender, get_i18n

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, user_service, state_manager, user_exists: bool, user_language: str):
    """
    /start buyrug'i handleri.
    
    Yangi user bo'lsa - til tanlash sahifasiga
    Mavjud user bo'lsa - bosh sahifaga
    """
    user_id = str(message.from_user.id)
    
    if not user_exists:
        # Yangi user - til tanlash
        render = LanguagePageRender(get_i18n("uz"))
        sent = await message.answer(
            text=render.get_text(),
            reply_markup=render.get_keyboard()
        )
        
        # State yaratish
        user_state = state_manager.create_user_state(user_id, message.chat.id)
        user_state.navigation.push("LANGUAGE_SELECTION")
        user_state.message_id = sent.message_id
    else:
        # Mavjud user - bosh sahifa
        i18n = get_i18n(user_language)
        render = HomePageRender(i18n)
        sent = await message.answer(
            text=render.get_text(),
            reply_markup=render.get_keyboard()
        )
        
        # State yaratish/yangilash
        user_state = state_manager.get_user_state(user_id)
        if not user_state:
            user_state = state_manager.create_user_state(user_id, message.chat.id)
        user_state.navigation.reset("HOME")
        user_state.message_id = sent.message_id
