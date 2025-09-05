"""
Media handlers for the Nutrition Bot (photos, barcodes)
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, PhotoSize
from aiogram.fsm.context import FSMContext

from services.database_service import DatabaseService
from services.vercel_api import VercelAPIService
from utils.keyboards import get_main_menu_keyboard
from utils.helpers import format_barcode_result

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.photo)
async def handle_photo(message: Message, db_service: DatabaseService, state: FSMContext) -> None:
    """Handle photo messages (barcode scanning or food analysis)"""
    try:
        # Get the largest photo
        photo: PhotoSize = message.photo[-1]
        
        # Download photo
        bot = message.bot
        file_info = await bot.get_file(photo.file_id)
        photo_bytes = await bot.download_file(file_info.file_path)
        
        # Convert to base64
        import base64
        photo_base64 = base64.b64encode(photo_bytes.read()).decode('utf-8')
        
        # Send processing message
        processing_msg = await message.answer("🔄 Обрабатываю изображение...")
        
        # Initialize Vercel API service
        vercel_api = VercelAPIService()
        
        # Try barcode detection first
        barcode_result = await vercel_api.process_barcode(photo_base64)
        
        if barcode_result and not barcode_result.get('error'):
            # Barcode found
            await processing_msg.delete()
            
            result_text = format_barcode_result(barcode_result)
            
            # If product found, save to database
            if barcode_result.get('found_in_database') and barcode_result.get('product'):
                user = await db_service.get_user_by_telegram_id(message.from_user.id)
                if user:
                    product = barcode_result['product']
                    # Ask for quantity
                    await message.answer(
                        f"{result_text}\n\n"
                        "💡 Укажите количество в граммах для добавления в дневник питания"
                    )
                    return
            
            await message.answer(result_text, reply_markup=get_main_menu_keyboard())
            return
        
        # Try food photo analysis
        photo_result = await vercel_api.analyze_photo(
            photo_base64, 
            "Проанализируй это фото еды и определи порции"
        )
        
        await processing_msg.delete()
        
        if photo_result and not photo_result.get('error'):
            # Food analysis successful
            food_items = photo_result.get('food_items', [])
            reference_object = photo_result.get('reference_object', {})
            
            if food_items:
                result_text = "🍽️ <b>Анализ блюда:</b>\n\n"
                
                total_calories = 0
                total_proteins = 0
                total_fats = 0
                total_carbs = 0
                
                for item in food_items:
                    name = item.get('name', 'Неизвестное блюдо')
                    weight = item.get('estimated_weight', 0)
                    nutrition = item.get('nutrition_estimate', {})
                    confidence = item.get('confidence', 0)
                    
                    calories = nutrition.get('calories', 0)
                    proteins = nutrition.get('proteins', 0)
                    fats = nutrition.get('fats', 0)
                    carbs = nutrition.get('carbs', 0)
                    
                    total_calories += calories
                    total_proteins += proteins
                    total_fats += fats
                    total_carbs += carbs
                    
                    result_text += (
                        f"• <b>{name}</b>\n"
                        f"  ⚖️ ~{weight:.0f}г (уверенность: {confidence*100:.0f}%)\n"
                        f"  🔥 {calories:.0f} ккал | "
                        f"🥩 {proteins:.1f}б | "
                        f"🧈 {fats:.1f}ж | "
                        f"🍞 {carbs:.1f}у\n\n"
                    )
                
                # Reference object info
                if reference_object.get('name'):
                    result_text += f"📏 <b>Эталонный объект:</b> {reference_object['name']}\n\n"
                
                # Total nutrition
                result_text += (
                    f"📊 <b>Итого:</b>\n"
                    f"🔥 {total_calories:.0f} ккал\n"
                    f"🥩 Белки: {total_proteins:.1f}г\n"
                    f"🧈 Жиры: {total_fats:.1f}г\n"
                    f"🍞 Углеводы: {total_carbs:.1f}г\n\n"
                    f"💡 <i>Это приблизительная оценка. Вы можете скорректировать данные.</i>"
                )
                
                # Save to database
                user = await db_service.get_user_by_telegram_id(message.from_user.id)
                if user and food_items:
                    for item in food_items:
                        nutrition = item.get('nutrition_estimate', {})
                        await db_service.add_food_log(
                            user_id=user.id,
                            product_name=item.get('name', 'Блюдо с фото'),
                            quantity_g=item.get('estimated_weight', 100),
                            calories=nutrition.get('calories', 0),
                            proteins=nutrition.get('proteins', 0),
                            fats=nutrition.get('fats', 0),
                            carbs=nutrition.get('carbs', 0),
                            source='photo'
                        )
                
                await message.answer(result_text, reply_markup=get_main_menu_keyboard())
            else:
                await message.answer(
                    "❌ Не удалось распознать еду на фото.\n\n"
                    "Попробуйте:\n"
                    "• Сделать фото более четким\n"
                    "• Добавить эталонный объект (монета, ложка)\n"
                    "• Улучшить освещение",
                    reply_markup=get_main_menu_keyboard()
                )
        else:
            # Both analyses failed
            error_msg = photo_result.get('error', 'Неизвестная ошибка') if photo_result else 'Сервис недоступен'
            await message.answer(
                f"❌ Не удалось обработать изображение.\n\n"
                f"Ошибка: {error_msg}\n\n"
                "Попробуйте:\n"
                "• Сделать новое фото\n"
                "• Проверить качество изображения\n"
                "• Повторить попытку позже",
                reply_markup=get_main_menu_keyboard()
            )
        
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке фото",
            reply_markup=get_main_menu_keyboard()
        )


def register_media_handlers(dp: Router) -> None:
    """Register media handlers"""
    dp.include_router(router)
