"""Statistics callback handler.

Statistika sahifasi callback'larini qayta ishlash.
"""
import io
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile

from src.presentation.renders import get_i18n
from src.presentation.renders.page import StatisticsPageRender
from src.core.services import StatisticsService

router = Router(name="statistics")


@router.callback_query(F.data == "page:statistics")
async def on_statistics(callback: CallbackQuery, user_service, quiz_service, 
                        state_manager, user_language: str):
    """
    Statistika sahifasini ko'rsatish.
    """
    user_id = callback.from_user.id
    user_id_str = str(user_id)
    i18n = get_i18n(user_language)
    
    # User ma'lumotlarini olish
    user = await user_service.get_user(user_id)
    user_name = user.name if user else callback.from_user.full_name
    
    # Statistikani olish
    total_stats = await quiz_service.get_user_total_stats(user_id)
    
    # Service yaratish
    stats_service = StatisticsService()
    summary = stats_service.calculate_summary(total_stats)
    
    # Render yaratish
    render = StatisticsPageRender(i18n, user_name, summary)
    
    # Navigation yangilash
    user_state = state_manager.get_user_state(user_id_str)
    if user_state:
        user_state.navigation.push("STATISTICS")
    
    # Agar natijalar bo'lsa, grafik bilan yuborish
    if summary["total_games"] > 0:
        # Oxirgi 30 kunlik ma'lumotlarni olish
        days = 30
        progress_list = await quiz_service.get_user_statistics(user_id, days)
        
        # Grafik yaratish
        chart_bytes = stats_service.generate_chart(progress_list, days)
        
        if chart_bytes:
            # Avvalgi xabarni o'chirish
            await callback.message.delete()
            
            # Rasm bilan yuborish
            photo = BufferedInputFile(chart_bytes, filename="statistics.png")
            await callback.message.answer_photo(
                photo=photo,
                caption=render.get_text(),
                reply_markup=render.get_keyboard()
            )
        else:
            # Grafiksiz yuborish (matplotlib yo'q bo'lsa)
            await callback.message.edit_text(
                text=render.get_text(),
                reply_markup=render.get_keyboard()
            )
    else:
        # Natijalar yo'q
        await callback.message.edit_text(
            text=render.get_text(),
            reply_markup=render.get_keyboard()
        )
    
    await callback.answer()
