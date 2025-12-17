"""Name input message handler.

Ism o'zgartirish uchun matn qabul qilish.
"""
from aiogram import Router, F
from aiogram.types import Message

from src.presentation.renders import SettingsPageRender, get_i18n

router = Router(name="name_input")


@router.message(F.text)
async def on_name_input(message: Message, user_service, state_manager, user_language: str):
    """
    Ism kiritish message handleri.
    
    Faqat WAITING_NAME holatida ishlaydi.
    """
    user_id = message.from_user.id
    user_id_str = str(user_id)
    
    user_state = state_manager.get_user_state(user_id_str)
    if not user_state:
        return
    
    current_page = user_state.navigation.get_current_page()
    if not current_page or current_page.type != "WAITING_NAME":
        return
    
    # Ismni yangilash
    new_name = message.text.strip()
    await user_service.update_name(user_id, new_name)
    
    i18n = get_i18n(user_language)
    
    # Xabar yuborish
    await message.answer(i18n.get("name_changed", name=new_name))
    
    # Sozlamalar sahifasiga qaytish
    render = SettingsPageRender(i18n)
    sent = await message.answer(
        text=render.get_text(),
        reply_markup=render.get_keyboard()
    )
    
    # Navigation yangilash
    user_state.navigation.pop()  # WAITING_NAME dan chiqish
    user_state.message_id = sent.message_id
