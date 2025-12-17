"""Quiz callback handler.

Quiz bilan bog'liq callback'larni qayta ishlash.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.presentation.renders import (
    QuestionPageRender,
    ResultPageRender,
    get_i18n,
)

router = Router(name="quiz")


@router.callback_query(F.data.startswith("level:"))
async def on_level_select(callback: CallbackQuery, quiz_service, state_manager, user_language: str):
    """
    Level tanlash callback handleri.
    
    callback_data format: "level:addition:1"
    """
    parts = callback.data.split(":")
    operation = parts[1]
    level = int(parts[2])
    user_id_str = str(callback.from_user.id)
    i18n = get_i18n(user_language)
    
    # Birinchi savolni generatsiya qilish
    question = quiz_service.generate_question(operation, level)
    total_questions = quiz_service.get_questions_count(level)
    
    render = QuestionPageRender(i18n, question, current=1, total=total_questions)
    
    await callback.message.edit_text(
        text=render.get_text(),
        reply_markup=render.get_keyboard()
    )
    
    # Navigation va quiz state yangilash
    user_state = state_manager.get_user_state(user_id_str)
    if user_state:
        user_state.navigation.push("QUESTION", {
            "operation": operation,
            "level": level,
            "current_question": 1,
            "total_questions": total_questions,
            "correct_answers": 0,
            "current_correct_answer": question.correct_answer,
        })
    
    await callback.answer()


@router.callback_query(F.data.startswith("answer:"))
async def on_answer(callback: CallbackQuery, quiz_service, state_manager, user_language: str):
    """
    Javob tanlash callback handleri.
    
    callback_data format: "answer:42"
    """
    user_answer = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    user_id_str = str(user_id)
    i18n = get_i18n(user_language)
    
    user_state = state_manager.get_user_state(user_id_str)
    if not user_state:
        await callback.answer("Session expired. Please /start again.")
        return
    
    current_page = user_state.navigation.get_current_page()
    if not current_page or current_page.type != "QUESTION":
        await callback.answer("Invalid state")
        return
    
    quiz_state = current_page.state
    correct_answer = quiz_state.get("current_correct_answer")
    is_correct = user_answer == correct_answer
    
    # Natijani hisoblash
    correct_answers = quiz_state.get("correct_answers", 0)
    if is_correct:
        correct_answers += 1
        await callback.answer(i18n.get("correct_answer"))
    else:
        await callback.answer(i18n.get("wrong_answer", correct=correct_answer))
    
    current_question = quiz_state.get("current_question", 1)
    total_questions = quiz_state.get("total_questions", 5)
    operation = quiz_state.get("operation")
    level = quiz_state.get("level")
    
    if current_question >= total_questions:
        # Quiz tugadi - natijani ko'rsatish
        await quiz_service.save_progress(
            user_id=user_id,
            operation=operation,
            level=level,
            correct_answers=correct_answers,
            total_questions=total_questions
        )
        
        render = ResultPageRender(i18n, operation, level, correct_answers, total_questions)
        await callback.message.edit_text(
            text=render.get_text(),
            reply_markup=render.get_keyboard()
        )
        
        user_state.navigation.replace("RESULT", {
            "operation": operation,
            "level": level,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
        })
    else:
        # Keyingi savol
        next_question = current_question + 1
        question = quiz_service.generate_question(operation, level)
        
        render = QuestionPageRender(i18n, question, next_question, total_questions)
        await callback.message.edit_text(
            text=render.get_text(),
            reply_markup=render.get_keyboard()
        )
        
        # State yangilash
        user_state.navigation.update_current_page_state({
            "current_question": next_question,
            "correct_answers": correct_answers,
            "current_correct_answer": question.correct_answer,
        })
