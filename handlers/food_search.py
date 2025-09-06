"""
Food search handlers for the Nutrition Bot
"""
import logging
from aiogram import Router, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.database_service import DatabaseService
from services.openfoodfacts import OpenFoodFactsService
from utils.helpers import parse_food_query, format_product_info
from utils.keyboards import get_main_menu_keyboard, get_search_keyboard, get_product_selection_keyboard, get_quantity_keyboard
from utils.i18n import get_text, Language

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "search_products")
async def search_products_callback(callback: CallbackQuery, user_language: Language) -> None:
    """Handle search products callback"""
    try:
        await callback.message.edit_text(
            get_text("search_instruction", user_language),
            reply_markup=get_search_keyboard(user_language)
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in search products callback: {e}")
        await callback.answer(get_text("error_general", user_language))


@router.callback_query(F.data == "search_by_name")
async def search_by_name_callback(callback: CallbackQuery, user_language: Language) -> None:
    """Handle search by name callback"""
    try:
        await callback.message.edit_text(
            get_text("search_by_name_instruction", user_language),
            reply_markup=get_main_menu_keyboard(user_language)
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in search by name callback: {e}")
        await callback.answer(get_text("error_general", user_language))


@router.message(F.text & ~F.text.startswith('/'))
async def handle_food_search(message: Message, db_service: DatabaseService, state: FSMContext, user_language: Language) -> None:
    """Handle food search queries"""
    try:
        # Parse the food query
        product_name, quantity = parse_food_query(message.text)
        
        if not product_name:
            await message.answer(
                get_text("product_not_recognized", user_language),
                reply_markup=get_main_menu_keyboard(user_language)
            )
            return
        
        if not quantity:
            quantity = 100  # Default quantity
        
        # Show searching message
        search_msg = await message.answer(
            get_text("searching_product", user_language).format(product=product_name)
        )
        
        # Search for product
        openfoodfacts = OpenFoodFactsService()
        products = await openfoodfacts.search_products(product_name)
        
        if not products:
            await search_msg.edit_text(
                get_text("product_not_found", user_language).format(product=product_name),
                reply_markup=get_main_menu_keyboard(user_language)
            )
            return
        
        # Use first product
        product = products[0]
        
        # Calculate nutrition for specified quantity
        calories = product.get('calories_per_100g', 0) * quantity / 100
        proteins = product.get('proteins_per_100g', 0) * quantity / 100
        fats = product.get('fats_per_100g', 0) * quantity / 100
        carbs = product.get('carbs_per_100g', 0) * quantity / 100
        
        # Format product info
        product_info = f"🍽️ <b>{product.get('name', 'Unknown Product')}</b>\n"
        product_info += f"⚖️ {quantity}г\n\n"
        product_info += get_text("nutrition_summary", user_language).format(
            calories=calories,
            proteins=proteins,
            fats=fats,
            carbs=carbs
        )
        
        # Save to database
        user = await db_service.get_user_by_telegram_id(message.from_user.id)
        if user:
            await db_service.add_food_log(
                user_id=user.id,
                product_name=product.get('name', 'Unknown Product'),
                quantity_g=quantity,
                calories=calories,
                proteins=proteins,
                fats=fats,
                carbs=carbs,
                source='search'
            )
        
        await search_msg.edit_text(
            get_text("product_added", user_language) + f"\n\n{product_info}",
            reply_markup=get_main_menu_keyboard(user_language)
        )
        
    except Exception as e:
        logger.error(f"Error in food search: {e}")
        await message.answer(
            get_text("error_search", user_language),
            reply_markup=get_main_menu_keyboard(user_language)
        )


def register_food_search_handlers(dp: Dispatcher) -> None:
    """Register food search handlers"""
    dp.include_router(router)
