"""
Basic command handlers for the Nutrition Bot
"""
import logging
from datetime import datetime, date
from typing import Dict, Any

from aiogram import Router, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.database_service import DatabaseService
from utils.keyboards import get_main_menu_keyboard, get_settings_keyboard, get_language_selection_keyboard
from utils.helpers import format_nutrition_summary, format_user_stats
from utils.validators import validate_calories_goal
from utils.i18n import get_text, Language

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, db_service: DatabaseService, state: FSMContext, user_language: Language) -> None:
    """Handle /start command"""
    try:
        user = message.from_user
        
        # Create or get user
        db_user = await db_service.create_or_get_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code or "en"
        )
        
        # Clear any existing state
        await state.clear()
        
        welcome_text = get_text("welcome_message", user_language).format(
            name=db_user.display_name,
            daily_goal=db_user.daily_goal_calories
        )
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_keyboard(user_language)
        )
        
        logger.info(f"User {user.id} started the bot")
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer(
            get_text("error_start", user_language),
            reply_markup=get_main_menu_keyboard(user_language)
        )


@router.message(Command("help"))
async def help_command(message: Message, user_language: Language) -> None:
    """Handle /help command"""
    help_text = get_text("help_message", user_language)
    
    await message.answer(help_text, reply_markup=get_main_menu_keyboard(user_language))


@router.message(Command("stats"))
async def stats_command(message: Message, db_service: DatabaseService, user_language: Language) -> None:
    """Handle /stats command"""
    try:
        user_id = message.from_user.id
        today = date.today()
        
        # Get user
        user = await db_service.get_user_by_telegram_id(user_id)
        if not user:
            await message.answer(get_text("error_user_not_found", user_language))
            return
        
        # Get today's stats
        today_stats = await db_service.get_daily_nutrition_summary(user.id, today)
        
        # Get weekly stats
        week_stats = await db_service.get_weekly_nutrition_summary(user.id)
        
        # Format stats
        stats_text = format_user_stats(user, today_stats, week_stats, user_language)
        
        await message.answer(stats_text, reply_markup=get_main_menu_keyboard(user_language))
        
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.answer(get_text("error_stats", user_language))


@router.message(Command("goal"))
async def goal_command(message: Message, db_service: DatabaseService, user_language: Language) -> None:
    """Handle /goal command"""
    try:
        # Parse goal from command
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(get_text("goal_help", user_language))
            return
        
        try:
            calories = int(args[0])
            if not validate_calories_goal(calories):
                await message.answer(get_text("error_invalid_goal", user_language))
                return
        except ValueError:
            await message.answer(get_text("error_invalid_number", user_language))
            return
        
        # Update user goal
        user_id = message.from_user.id
        success = await db_service.update_user_goal(user_id, calories)
        
        if success:
            await message.answer(
                get_text("goal_updated", user_language).format(calories=calories)
            )
        else:
            await message.answer(get_text("error_goal_update", user_language))
            
    except Exception as e:
        logger.error(f"Error in goal command: {e}")
        await message.answer(get_text("error_goal_set", user_language))


@router.message(Command("history"))
async def history_command(message: Message, db_service: DatabaseService, user_language: Language) -> None:
    """Handle /history command"""
    try:
        user_id = message.from_user.id
        
        # Get user
        user = await db_service.get_user_by_telegram_id(user_id)
        if not user:
            await message.answer(get_text("error_user_not_found", user_language))
            return
        
        # Get recent food logs
        recent_logs = await db_service.get_recent_food_logs(user.id, limit=10)
        
        if not recent_logs:
            await message.answer(get_text("history_empty", user_language))
            return
        
        history_text = get_text("history_header", user_language) + "\n\n"
        
        for log in recent_logs:
            date_str = log.logged_at.strftime("%d.%m %H:%M")
            history_text += get_text("history_entry", user_language).format(
                date=date_str,
                product=log.product_name,
                quantity=log.quantity_g,
                calories=log.calories,
                proteins=log.proteins,
                fats=log.fats,
                carbs=log.carbs
            ) + "\n\n"
        
        await message.answer(history_text)
        
    except Exception as e:
        logger.error(f"Error in history command: {e}")
        await message.answer(get_text("error_history", user_language))


@router.message(Command("clear"))
async def clear_command(message: Message, db_service: DatabaseService, user_language: Language) -> None:
    """Handle /clear command"""
    try:
        user_id = message.from_user.id
        today = date.today()
        
        # Get user
        user = await db_service.get_user_by_telegram_id(user_id)
        if not user:
            await message.answer(get_text("error_user_not_found", user_language))
            return
        
        # Get today's logs count
        logs_count = await db_service.get_daily_logs_count(user.id, today)
        
        if logs_count == 0:
            await message.answer(get_text("clear_no_data", user_language))
            return
        
        # Clear today's logs
        deleted_count = await db_service.clear_daily_logs(user.id, today)
        
        await message.answer(
            get_text("clear_success", user_language).format(
                count=deleted_count,
                date=today.strftime('%d.%m.%Y')
            )
        )
        
    except Exception as e:
        logger.error(f"Error in clear command: {e}")
        await message.answer(get_text("error_clear", user_language))


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, user_language: Language) -> None:
    """Handle main menu callback"""
    await callback.message.edit_text(
        get_text("main_menu", user_language),
        reply_markup=get_main_menu_keyboard(user_language)
    )
    await callback.answer()


@router.callback_query(F.data == "settings")
async def settings_callback(callback: CallbackQuery, db_service: DatabaseService, user_language: Language) -> None:
    """Handle settings callback"""
    try:
        user_id = callback.from_user.id
        user = await db_service.get_user_by_telegram_id(user_id)
        
        if not user:
            await callback.answer(get_text("error_user_not_found", user_language))
            return
        
        settings_text = get_text("settings_info", user_language).format(
            name=user.display_name,
            daily_goal=user.daily_goal_calories,
            language=user.language_code.upper(),
            registration_date=user.created_at.strftime('%d.%m.%Y')
        )
        
        await callback.message.edit_text(
            settings_text,
            reply_markup=get_settings_keyboard(user_language)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in settings callback: {e}")
        await callback.answer(get_text("error_settings", user_language))


@router.message(Command("lang"))
async def lang_command(message: Message, user_language: Language) -> None:
    """Handle /lang command"""
    await message.answer(
        get_text("language_selection", user_language),
        reply_markup=get_language_selection_keyboard()
    )


@router.callback_query(F.data == "change_language")
async def change_language_callback(callback: CallbackQuery, user_language: Language) -> None:
    """Handle change language callback"""
    await callback.message.edit_text(
        get_text("language_selection", user_language),
        reply_markup=get_language_selection_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lang_"))
async def language_selection_callback(callback: CallbackQuery, db_service: DatabaseService) -> None:
    """Handle language selection callback"""
    try:
        # Extract language code from callback data
        lang_code = callback.data.split("_")[1]  # lang_en -> en
        
        # Map language codes to Language enum
        language_map = {
            "en": Language.EN,
            "ru": Language.RU,
            "uk": Language.UK
        }
        
        if lang_code not in language_map:
            await callback.answer("❌ Invalid language")
            return
        
        new_language = language_map[lang_code]
        user_id = callback.from_user.id
        
        # Update user language in database
        success = await db_service.update_user_language(user_id, lang_code)
        
        if success:
            await callback.message.edit_text(
                get_text("language_changed", new_language),
                reply_markup=get_main_menu_keyboard(new_language)
            )
        else:
            await callback.message.edit_text(
                get_text("error_language_change", new_language),
                reply_markup=get_main_menu_keyboard(new_language)
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in language selection: {e}")
        await callback.answer("❌ Error changing language")


def register_basic_handlers(dp: Dispatcher) -> None:
    """Register basic handlers"""
    dp.include_router(router)
