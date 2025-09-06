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
        
        # Search for product with fallback
        openfoodfacts = OpenFoodFactsService()
        try:
            products = await openfoodfacts.search_products(product_name)
        except Exception as e:
            logger.error(f"OpenFoodFacts API error: {e}")
            products = []
        
        if not products:
            # Fallback: use basic nutrition estimates
            basic_nutrition = _get_basic_nutrition_estimate(product_name, quantity)
            if basic_nutrition:
                product = basic_nutrition
                await search_msg.edit_text(
                    get_text("product_added", user_language) + f"\n\n🍽️ <b>{product['name']}</b>\n⚖️ {quantity}г\n\n" +
                    get_text("nutrition_summary", user_language).format(
                        calories=product['calories_per_100g'] * quantity / 100,
                        proteins=product['proteins_per_100g'] * quantity / 100,
                        fats=product['fats_per_100g'] * quantity / 100,
                        carbs=product['carbs_per_100g'] * quantity / 100
                    ) + "\n\n💡 <i>Приблизительные данные (API недоступен)</i>",
                    reply_markup=get_main_menu_keyboard(user_language)
                )
                
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
                        source='fallback'
                    )
                return
            else:
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


def _get_basic_nutrition_estimate(product_name: str, quantity: float) -> dict:
    """Get basic nutrition estimates for common foods when API is unavailable"""
    product_name_lower = product_name.lower()
    
    # Basic nutrition database (per 100g)
    basic_foods = {
        # Fruits
        'яблоко': {'calories': 52, 'proteins': 0.3, 'fats': 0.2, 'carbs': 14},
        'apple': {'calories': 52, 'proteins': 0.3, 'fats': 0.2, 'carbs': 14},
        'банан': {'calories': 89, 'proteins': 1.1, 'fats': 0.3, 'carbs': 23},
        'banana': {'calories': 89, 'proteins': 1.1, 'fats': 0.3, 'carbs': 23},
        'апельсин': {'calories': 47, 'proteins': 0.9, 'fats': 0.1, 'carbs': 12},
        'orange': {'calories': 47, 'proteins': 0.9, 'fats': 0.1, 'carbs': 12},
        
        # Vegetables
        'помидор': {'calories': 18, 'proteins': 0.9, 'fats': 0.2, 'carbs': 3.9},
        'tomato': {'calories': 18, 'proteins': 0.9, 'fats': 0.2, 'carbs': 3.9},
        'огурец': {'calories': 16, 'proteins': 0.7, 'fats': 0.1, 'carbs': 4.1},
        'cucumber': {'calories': 16, 'proteins': 0.7, 'fats': 0.1, 'carbs': 4.1},
        'морковь': {'calories': 41, 'proteins': 0.9, 'fats': 0.2, 'carbs': 10},
        'carrot': {'calories': 41, 'proteins': 0.9, 'fats': 0.2, 'carbs': 10},
        
        # Grains
        'рис': {'calories': 130, 'proteins': 2.7, 'fats': 0.3, 'carbs': 28},
        'rice': {'calories': 130, 'proteins': 2.7, 'fats': 0.3, 'carbs': 28},
        'гречка': {'calories': 343, 'proteins': 13.3, 'fats': 3.4, 'carbs': 62},
        'buckwheat': {'calories': 343, 'proteins': 13.3, 'fats': 3.4, 'carbs': 62},
        'хлеб': {'calories': 265, 'proteins': 9, 'fats': 3.2, 'carbs': 49},
        'bread': {'calories': 265, 'proteins': 9, 'fats': 3.2, 'carbs': 49},
        
        # Proteins
        'курица': {'calories': 165, 'proteins': 31, 'fats': 3.6, 'carbs': 0},
        'chicken': {'calories': 165, 'proteins': 31, 'fats': 3.6, 'carbs': 0},
        'говядина': {'calories': 250, 'proteins': 26, 'fats': 15, 'carbs': 0},
        'beef': {'calories': 250, 'proteins': 26, 'fats': 15, 'carbs': 0},
        'яйцо': {'calories': 155, 'proteins': 13, 'fats': 11, 'carbs': 1.1},
        'egg': {'calories': 155, 'proteins': 13, 'fats': 11, 'carbs': 1.1},
        
        # Dairy
        'молоко': {'calories': 42, 'proteins': 3.4, 'fats': 1, 'carbs': 5},
        'milk': {'calories': 42, 'proteins': 3.4, 'fats': 1, 'carbs': 5},
        'творог': {'calories': 103, 'proteins': 18, 'fats': 0.6, 'carbs': 3.3},
        'cottage cheese': {'calories': 103, 'proteins': 18, 'fats': 0.6, 'carbs': 3.3},
        'сыр': {'calories': 402, 'proteins': 25, 'fats': 33, 'carbs': 0.3},
        'cheese': {'calories': 402, 'proteins': 25, 'fats': 33, 'carbs': 0.3},
    }
    
    # Try exact match first
    if product_name_lower in basic_foods:
        nutrition = basic_foods[product_name_lower]
        return {
            'name': product_name.title(),
            'calories_per_100g': nutrition['calories'],
            'proteins_per_100g': nutrition['proteins'],
            'fats_per_100g': nutrition['fats'],
            'carbs_per_100g': nutrition['carbs']
        }
    
    # Try partial match
    for food_name, nutrition in basic_foods.items():
        if food_name in product_name_lower or product_name_lower in food_name:
            return {
                'name': product_name.title(),
                'calories_per_100g': nutrition['calories'],
                'proteins_per_100g': nutrition['proteins'],
                'fats_per_100g': nutrition['fats'],
                'carbs_per_100g': nutrition['carbs']
            }
    
    # Default fallback for unknown products
    return {
        'name': product_name.title(),
        'calories_per_100g': 100,  # Average estimate
        'proteins_per_100g': 5,
        'fats_per_100g': 3,
        'carbs_per_100g': 15
    }


def register_food_search_handlers(dp: Dispatcher) -> None:
    """Register food search handlers"""
    dp.include_router(router)
