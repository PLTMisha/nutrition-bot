"""
Food search handlers for the Nutrition Bot
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.database_service import DatabaseService
from services.openfoodfacts import OpenFoodFactsService
from utils.helpers import parse_food_query, format_product_info
from utils.keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text & ~F.text.startswith('/'))
async def handle_food_search(message: Message, db_service: DatabaseService, state: FSMContext) -> None:
    """Handle food search queries"""
    try:
        # Parse the food query
        product_name, quantity = parse_food_query(message.text)
        
        if not product_name:
            await message.answer(
                "❌ Не удалось распознать продукт.\n\n"
                "Попробуйте написать так:\n"
                "• яблоко 150г\n"
                "• хлеб 50г\n"
                "• молоко 200мл",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        if not quantity:
            quantity = 100  # Default quantity
        
        # Search for product
        openfoodfacts = OpenFoodFactsService()
        products = await openfoodfacts.search_products(product_name)
        
        if not products:
            await message.answer(
                f"❌ Продукт '{product_name}' не найден.\n\n"
                "Попробуйте:\n"
                "• Изменить название\n"
                "• Использовать английское название\n"
                "• Сфотографировать штрих-код",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        # Use first product
        product = products[0]
        
        # Format product info
        product_info = format_product_info(product, quantity)
        
        # Save to database
        user = await db_service.get_user_by_telegram_id(message.from_user.id)
        if user:
            await db_service.add_food_log(
                user_id=user.id,
                product_name=product['name'],
                quantity_g=quantity,
                calories=product['calories_per_100g'] * quantity / 100,
                proteins=product['proteins_per_100g'] * quantity / 100,
                fats=product['fats_per_100g'] * quantity / 100,
                carbs=product['carbs_per_100g'] * quantity / 100,
                source='search'
            )
        
        await message.answer(
            f"✅ <b>Продукт добавлен!</b>\n\n{product_info}",
            reply_markup=get_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in food search: {e}")
        await message.answer(
            "❌ Произошла ошибка при поиске продукта",
            reply_markup=get_main_menu_keyboard()
        )


def register_food_search_handlers(dp: Router) -> None:
    """Register food search handlers"""
    dp.include_router(router)
