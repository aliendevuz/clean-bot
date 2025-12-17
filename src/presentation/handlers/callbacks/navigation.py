"""Navigation callback handler.

Sahifalar orasidagi navigatsiyani boshqarish.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.presentation.renders import (
    HomePageRender,
    SettingsPageRender,
    LanguagePageRender,
    LevelListPageRender,
    get_i18n,
)

router = Router(name="navigation")


@router.callback_query(F.data.startswith("page:"))
async def on_page_navigate(callback: CallbackQuery, state_manager, user_language: str):
    """
    Sahifaga o'tish callback handleri.
    
    callback_data format: "page:home" | "page:settings"
    """
    page = callback.data.split(":")[1]
    user_id_str = str(callback.from_user.id)
    i18n = get_i18n(user_language)
    
    user_state = state_manager.get_user_state(user_id_str)
    
    if page == "home":
        render = HomePageRender(i18n)
        if user_state:
            user_state.navigation.reset("HOME")
    elif page == "settings":
        render = SettingsPageRender(i18n)
        if user_state:
            user_state.navigation.push("SETTINGS")
    else:
        await callback.answer("Unknown page")
        return
    
    # Agar xabar rasm bo'lsa (statistika sahifasidan qaytganda)
    # edit_text ishlamaydi, edit_caption ishlatamiz
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            text=render.get_text(),
            reply_markup=render.get_keyboard()
        )
    else:
        await callback.message.edit_text(
            text=render.get_text(),
            reply_markup=render.get_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data.startswith("op:"))
async def on_operation_select(callback: CallbackQuery, state_manager, user_language: str):
    """
    Operatsiya tanlash callback handleri.
    
    callback_data format: "op:addition" | "op:subtraction" etc.
    """
    operation = callback.data.split(":")[1]
    user_id_str = str(callback.from_user.id)
    i18n = get_i18n(user_language)
    
    render = LevelListPageRender(i18n, operation)
    
    await callback.message.edit_text(
        text=render.get_text(),
        reply_markup=render.get_keyboard()
    )
    
    # Navigation yangilash
    user_state = state_manager.get_user_state(user_id_str)
    if user_state:
        user_state.navigation.push("LEVEL_LIST", {"operation": operation})
    
    await callback.answer()


@router.callback_query(F.data.startswith("action:"))
async def on_action(callback: CallbackQuery, state_manager, user_language: str):
    """
    Action callback handleri.
    
    callback_data format: "action:change_name" | "action:change_language"
    """
    action = callback.data.split(":")[1]
    user_id_str = str(callback.from_user.id)
    i18n = get_i18n(user_language)
    
    if action == "change_language":
        render = LanguagePageRender(i18n)
        await callback.message.edit_text(
            text=render.get_text(),
            reply_markup=render.get_keyboard()
        )
        
        user_state = state_manager.get_user_state(user_id_str)
        if user_state:
            user_state.navigation.push("LANGUAGE_SELECTION")
            
    elif action == "change_name":
        await callback.message.edit_text(
            text=i18n.get("enter_new_name")
        )
        
        user_state = state_manager.get_user_state(user_id_str)
        if user_state:
            user_state.navigation.push("WAITING_NAME")
    
    await callback.answer()
