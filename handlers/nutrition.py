"""
Nutrition tracking and statistics handlers for the Nutrition Bot
"""
import logging
from datetime import date, timedelta
from aiogram import Router, Dispatcher, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from services.database_service import DatabaseService
from utils.keyboards import get_main_menu_keyboard, get_stats_keyboard
from utils.helpers import format_user_stats, generate_nutrition_chart

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "view_stats")
async def view_stats_callback(callback: CallbackQuery, db_service: DatabaseService) -> None:
    """Handle view stats callback"""
    try:
        user_id = callback.from_user.id
        today = date.today()
        
        # Get user
        user = await db_service.get_user_by_telegram_id(user_id)
        if not user:
            await callback.answer("❌ Пользователь не найден")
            return
        
        # Get today's stats
        today_stats = await db_service.get_daily_nutrition_summary(user.id, today)
        
        # Get weekly stats
        week_stats = await db_service.get_weekly_nutrition_summary(user.id)
        
        # Format stats
        stats_text = format_user_stats(user, today_stats, week_stats)
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=get_stats_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in view stats callback: {e}")
        await callback.answer("❌ Ошибка при получении статистики")


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
