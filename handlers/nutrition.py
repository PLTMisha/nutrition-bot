"""
Nutrition tracking and statistics handlers for the Nutrition Bot
"""
import logging
from datetime import date, timedelta
from aiogram import Router, Dispatcher, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from services.database_service import DatabaseService
from utils.keyboards import get_main_menu_keyboard, get_stats_keyboard, get_stats_period_keyboard
from utils.helpers import format_user_stats, generate_nutrition_chart
from utils.i18n import get_text, Language

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "view_stats")
async def view_stats_callback(callback: CallbackQuery, db_service: DatabaseService, user_language: Language) -> None:
    """Handle view stats callback"""
    try:
        await callback.message.edit_text(
            get_text("view_stats", user_language),
            reply_markup=get_stats_period_keyboard(user_language)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in view stats callback: {e}")
        await callback.answer(get_text("error_general", user_language))


@router.callback_query(F.data == "show_history")
async def show_history_callback(callback: CallbackQuery, db_service: DatabaseService, user_language: Language) -> None:
    """Handle show history callback"""
    try:
        user_id = callback.from_user.id
        
        # Get user
        user = await db_service.get_user_by_telegram_id(user_id)
        if not user:
            await callback.answer(get_text("error_user_not_found", user_language))
            return
        
        # Get recent food logs
        recent_logs = await db_service.get_recent_food_logs(user.id, limit=10)
        
        if not recent_logs:
            await callback.message.edit_text(
                get_text("history_empty", user_language),
                reply_markup=get_main_menu_keyboard(user_language)
            )
            await callback.answer()
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
        
        await callback.message.edit_text(
            history_text,
            reply_markup=get_main_menu_keyboard(user_language)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in show history callback: {e}")
        await callback.answer(get_text("error_history", user_language))


@router.callback_query(F.data.startswith("stats_"))
async def stats_period_callback(callback: CallbackQuery, db_service: DatabaseService, user_language: Language) -> None:
    """Handle stats period selection callback"""
    try:
        period = callback.data.split("_")[1]  # stats_today -> today
        user_id = callback.from_user.id
        
        # Get user
        user = await db_service.get_user_by_telegram_id(user_id)
        if not user:
            await callback.answer(get_text("error_user_not_found", user_language))
            return
        
        today = date.today()
        
        if period == "today":
            # Get today's stats
            today_stats = await db_service.get_daily_nutrition_summary(user.id, today)
            week_stats = await db_service.get_weekly_nutrition_summary(user.id)
            
            # Format stats using i18n
            stats_text = get_text("stats_message", user_language).format(
                name=user.display_name,
                goal_calories=user.daily_goal_calories,
                progress_bar=_generate_progress_bar(today_stats.get('calories', 0), user.daily_goal_calories),
                progress_percent=(today_stats.get('calories', 0) / user.daily_goal_calories * 100) if user.daily_goal_calories > 0 else 0,
                today_calories=today_stats.get('calories', 0),
                today_entries=today_stats.get('entries', 0),
                remaining_calories=max(0, user.daily_goal_calories - today_stats.get('calories', 0)),
                week_calories=week_stats.get('calories', 0),
                avg_daily_calories=week_stats.get('calories', 0) / 7,
                week_entries=week_stats.get('entries', 0),
                nutrition_summary=get_text("nutrition_summary", user_language).format(
                    calories=today_stats.get('calories', 0),
                    proteins=today_stats.get('proteins', 0),
                    fats=today_stats.get('fats', 0),
                    carbs=today_stats.get('carbs', 0)
                )
            )
            
        elif period == "week":
            # Get weekly stats
            week_stats = await db_service.get_weekly_nutrition_summary(user.id)
            
            stats_text = get_text("stats_title", user_language) + "\n\n"
            stats_text += get_text("stats_user", user_language).format(name=user.display_name) + "\n"
            stats_text += get_text("stats_week", user_language) + "\n"
            stats_text += get_text("stats_total", user_language).format(calories=week_stats.get('calories', 0)) + "\n"
            stats_text += get_text("stats_average", user_language).format(calories=week_stats.get('calories', 0) / 7) + "\n"
            stats_text += get_text("stats_entries", user_language).format(count=week_stats.get('entries', 0)) + "\n\n"
            stats_text += get_text("nutrition_summary", user_language).format(
                calories=week_stats.get('calories', 0),
                proteins=week_stats.get('proteins', 0),
                fats=week_stats.get('fats', 0),
                carbs=week_stats.get('carbs', 0)
            )
            
        elif period == "month":
            # Get monthly stats
            month_stats = await db_service.get_monthly_nutrition_summary(user.id)
            
            stats_text = get_text("stats_title", user_language) + "\n\n"
            stats_text += get_text("stats_user", user_language).format(name=user.display_name) + "\n"
            
            month_text = {
                Language.EN: "📊 <b>This Month:</b>",
                Language.RU: "📊 <b>За месяц:</b>",
                Language.UK: "📊 <b>За місяць:</b>"
            }.get(user_language, "📊 <b>This Month:</b>")
            
            stats_text += month_text + "\n"
            stats_text += get_text("stats_total", user_language).format(calories=month_stats.get('calories', 0)) + "\n"
            stats_text += get_text("stats_average", user_language).format(calories=month_stats.get('calories', 0) / 30) + "\n"
            stats_text += get_text("stats_entries", user_language).format(count=month_stats.get('entries', 0)) + "\n\n"
            stats_text += get_text("nutrition_summary", user_language).format(
                calories=month_stats.get('calories', 0),
                proteins=month_stats.get('proteins', 0),
                fats=month_stats.get('fats', 0),
                carbs=month_stats.get('carbs', 0)
            )
            
        else:  # all time
            # Get all time stats
            all_stats = await db_service.get_all_time_nutrition_summary(user.id)
            
            stats_text = get_text("stats_title", user_language) + "\n\n"
            stats_text += get_text("stats_user", user_language).format(name=user.display_name) + "\n"
            
            all_time_text = {
                Language.EN: "📊 <b>All Time:</b>",
                Language.RU: "📊 <b>За все время:</b>",
                Language.UK: "📊 <b>За весь час:</b>"
            }.get(user_language, "📊 <b>All Time:</b>")
            
            stats_text += all_time_text + "\n"
            stats_text += get_text("stats_total", user_language).format(calories=all_stats.get('calories', 0)) + "\n"
            stats_text += get_text("stats_entries", user_language).format(count=all_stats.get('entries', 0)) + "\n\n"
            stats_text += get_text("nutrition_summary", user_language).format(
                calories=all_stats.get('calories', 0),
                proteins=all_stats.get('proteins', 0),
                fats=all_stats.get('fats', 0),
                carbs=all_stats.get('carbs', 0)
            )
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=get_stats_keyboard(user_language)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in stats period callback: {e}")
        await callback.answer(get_text("error_stats", user_language))


def _generate_progress_bar(current: float, goal: float, length: int = 10) -> str:
    """Generate progress bar"""
    if goal <= 0:
        return "▱" * length
    
    progress = min(current / goal, 1.0)
    filled = int(progress * length)
    empty = length - filled
    
    return "▰" * filled + "▱" * empty


@router.callback_query(F.data == "weekly_chart")
async def weekly_chart_callback(callback: CallbackQuery, db_service: DatabaseService) -> None:
    """Handle weekly chart callback"""
    try:
        user_id = callback.from_user.id
        
        # Get user
        user = await db_service.get_user_by_telegram_id(user_id)
        if not user:
            await callback.answer("❌ Пользователь не найден")
            return
        
        # Get weekly data
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        weekly_data = []
        current_date = start_date
        
        while current_date <= end_date:
            daily_stats = await db_service.get_daily_nutrition_summary(user.id, current_date)
            weekly_data.append({
                'date': current_date,
                'calories': daily_stats.get('calories', 0),
                'proteins': daily_stats.get('proteins', 0),
                'fats': daily_stats.get('fats', 0),
                'carbs': daily_stats.get('carbs', 0)
            })
            current_date += timedelta(days=1)
        
        # Generate chart
        chart_buffer = generate_nutrition_chart(weekly_data, 'неделю')
        
        if chart_buffer:
            # Send chart as photo
            chart_file = BufferedInputFile(
                chart_buffer.getvalue(),
                filename="nutrition_chart.png"
            )
            
            await callback.message.answer_photo(
                chart_file,
                caption="📊 <b>Статистика питания за неделю</b>",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await callback.message.answer(
                "❌ Не удалось создать график",
                reply_markup=get_main_menu_keyboard()
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error generating weekly chart: {e}")
        await callback.answer("❌ Ошибка при создании графика")


@router.callback_query(F.data == "monthly_chart")
async def monthly_chart_callback(callback: CallbackQuery, db_service: DatabaseService) -> None:
    """Handle monthly chart callback"""
    try:
        user_id = callback.from_user.id
        
        # Get user
        user = await db_service.get_user_by_telegram_id(user_id)
        if not user:
            await callback.answer("❌ Пользователь не найден")
            return
        
        # Get monthly data (last 30 days)
        end_date = date.today()
        start_date = end_date - timedelta(days=29)
        
        monthly_data = []
        current_date = start_date
        
        while current_date <= end_date:
            daily_stats = await db_service.get_daily_nutrition_summary(user.id, current_date)
            monthly_data.append({
                'date': current_date,
                'calories': daily_stats.get('calories', 0),
                'proteins': daily_stats.get('proteins', 0),
                'fats': daily_stats.get('fats', 0),
                'carbs': daily_stats.get('carbs', 0)
            })
            current_date += timedelta(days=1)
        
        # Generate chart
        chart_buffer = generate_nutrition_chart(monthly_data, 'месяц')
        
        if chart_buffer:
            # Send chart as photo
            chart_file = BufferedInputFile(
                chart_buffer.getvalue(),
                filename="nutrition_chart_monthly.png"
            )
            
            await callback.message.answer_photo(
                chart_file,
                caption="📊 <b>Статистика питания за месяц</b>",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await callback.message.answer(
                "❌ Не удалось создать график",
                reply_markup=get_main_menu_keyboard()
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error generating monthly chart: {e}")
        await callback.answer("❌ Ошибка при создании графика")


@router.callback_query(F.data == "export_data")
async def export_data_callback(callback: CallbackQuery, db_service: DatabaseService) -> None:
    """Handle export data callback"""
    try:
        user_id = callback.from_user.id
        
        # Get user
        user = await db_service.get_user_by_telegram_id(user_id)
        if not user:
            await callback.answer("❌ Пользователь не найден")
            return
        
        # Get all food logs for the user
        food_logs = await db_service.get_user_food_logs(user.id, limit=1000)
        
        if not food_logs:
            await callback.answer("❌ Нет данных для экспорта")
            return
        
        # Create CSV content
        csv_content = "Дата,Время,Продукт,Количество (г),Калории,Белки (г),Жиры (г),Углеводы (г),Источник\n"
        
        for log in food_logs:
            csv_content += (
                f"{log.date},{log.logged_at.strftime('%H:%M')},"
                f"{log.product_name},{log.quantity_g},"
                f"{log.calories:.1f},{log.proteins:.1f},"
                f"{log.fats:.1f},{log.carbs:.1f},{log.source}\n"
            )
        
        # Send CSV file
        csv_file = BufferedInputFile(
            csv_content.encode('utf-8-sig'),  # BOM for Excel compatibility
            filename=f"nutrition_data_{user.telegram_id}.csv"
        )
        
        await callback.message.answer_document(
            csv_file,
            caption="📊 <b>Экспорт данных питания</b>\n\nВаши данные в формате CSV",
            reply_markup=get_main_menu_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        await callback.answer("❌ Ошибка при экспорте данных")


@router.callback_query(F.data == "delete_last")
async def delete_last_callback(callback: CallbackQuery, db_service: DatabaseService) -> None:
    """Handle delete last entry callback"""
    try:
        user_id = callback.from_user.id
        
        # Get user
        user = await db_service.get_user_by_telegram_id(user_id)
        if not user:
            await callback.answer("❌ Пользователь не найден")
            return
        
        # Get last food log
        recent_logs = await db_service.get_recent_food_logs(user.id, limit=1)
        
        if not recent_logs:
            await callback.answer("❌ Нет записей для удаления")
            return
        
        last_log = recent_logs[0]
        
        # Delete the log
        success = await db_service.delete_food_log(last_log.id)
        
        if success:
            await callback.message.answer(
                f"✅ <b>Запись удалена</b>\n\n"
                f"🍽️ {last_log.product_name}\n"
                f"⚖️ {last_log.quantity_g}г\n"
                f"🔥 {last_log.calories:.0f} ккал",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await callback.message.answer(
                "❌ Не удалось удалить запись",
                reply_markup=get_main_menu_keyboard()
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error deleting last entry: {e}")
        await callback.answer("❌ Ошибка при удалении записи")


def register_nutrition_handlers(dp: Dispatcher) -> None:
    """Register nutrition handlers"""
    dp.include_router(router)
