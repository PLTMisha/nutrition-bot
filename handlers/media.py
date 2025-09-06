"""
Media handlers for the Nutrition Bot (photos, barcodes)
"""
import logging
from aiogram import Router, Dispatcher, F
from aiogram.types import Message, PhotoSize, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.database_service import DatabaseService
from services.vercel_api import VercelAPIService
from utils.keyboards import get_main_menu_keyboard, get_barcode_scan_keyboard, get_photo_analysis_keyboard
from utils.helpers import format_barcode_result
from utils.i18n import get_text, Language

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "scan_barcode")
async def scan_barcode_callback(callback: CallbackQuery, user_language: Language) -> None:
    """Handle scan barcode callback"""
    try:
        await callback.message.edit_text(
            get_text("barcode_instruction", user_language),
            reply_markup=get_barcode_scan_keyboard(user_language)
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in scan barcode callback: {e}")
        await callback.answer(get_text("error_general", user_language))


@router.callback_query(F.data == "barcode_instructions")
async def barcode_instructions_callback(callback: CallbackQuery, user_language: Language) -> None:
    """Handle barcode instructions callback"""
    try:
        await callback.message.edit_text(
            get_text("barcode_instructions", user_language),
            reply_markup=get_barcode_scan_keyboard(user_language)
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in barcode instructions callback: {e}")
        await callback.answer(get_text("error_general", user_language))


@router.callback_query(F.data == "analyze_photo")
async def analyze_photo_callback(callback: CallbackQuery, user_language: Language) -> None:
    """Handle analyze photo callback"""
    try:
        await callback.message.edit_text(
            get_text("photo_instruction", user_language),
            reply_markup=get_photo_analysis_keyboard(user_language)
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in analyze photo callback: {e}")
        await callback.answer(get_text("error_general", user_language))


@router.callback_query(F.data == "photo_instructions")
async def photo_instructions_callback(callback: CallbackQuery, user_language: Language) -> None:
    """Handle photo instructions callback"""
    try:
        await callback.message.edit_text(
            get_text("photo_instructions", user_language),
            reply_markup=get_photo_analysis_keyboard(user_language)
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in photo instructions callback: {e}")
        await callback.answer(get_text("error_general", user_language))


@router.callback_query(F.data == "reference_objects")
async def reference_objects_callback(callback: CallbackQuery, user_language: Language) -> None:
    """Handle reference objects callback"""
    try:
        await callback.message.edit_text(
            get_text("reference_objects", user_language),
            reply_markup=get_photo_analysis_keyboard(user_language)
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in reference objects callback: {e}")
        await callback.answer(get_text("error_general", user_language))


@router.callback_query(F.data == "photo_tips")
async def photo_tips_callback(callback: CallbackQuery, user_language: Language) -> None:
    """Handle photo tips callback"""
    try:
        await callback.message.edit_text(
            get_text("photo_tips", user_language),
            reply_markup=get_photo_analysis_keyboard(user_language)
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in photo tips callback: {e}")
        await callback.answer(get_text("error_general", user_language))


@router.message(F.photo)
async def handle_photo(message: Message, db_service: DatabaseService, state: FSMContext, user_language: Language) -> None:
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
        processing_msg = await message.answer(get_text("processing_image", user_language))
        
        # Initialize Vercel API service
        vercel_api = VercelAPIService()
        
        # Try barcode detection first
        barcode_result = await vercel_api.process_barcode(photo_base64)
        
        if barcode_result and not barcode_result.get('error'):
            # Barcode found
            await processing_msg.delete()
            
            barcode = barcode_result.get('barcode', 'Unknown')
            result_text = get_text("barcode_detected", user_language).format(barcode=barcode) + "\n\n"
            
            # If product found, save to database
            if barcode_result.get('found_in_database') and barcode_result.get('product'):
                product = barcode_result['product']
                result_text += get_text("product_found_db", user_language) + "\n\n"
                result_text += f"🍽️ <b>{product.get('name', 'Unknown Product')}</b>\n"
                result_text += get_text("nutrition_summary", user_language).format(
                    calories=product.get('calories_per_100g', 0),
                    proteins=product.get('proteins_per_100g', 0),
                    fats=product.get('fats_per_100g', 0),
                    carbs=product.get('carbs_per_100g', 0)
                ) + "\n\n"
                result_text += get_text("specify_quantity", user_language)
                
                await message.answer(result_text, reply_markup=get_main_menu_keyboard(user_language))
                return
            else:
                result_text += get_text("product_not_found_db", user_language)
            
            await message.answer(result_text, reply_markup=get_main_menu_keyboard(user_language))
            return
        
        # Try food photo analysis
        analysis_prompt = {
            Language.EN: "Analyze this food photo and determine portions",
            Language.RU: "Проанализируй это фото еды и определи порции",
            Language.UK: "Проаналізуй це фото їжі та визнач порції"
        }.get(user_language, "Analyze this food photo and determine portions")
        
        photo_result = await vercel_api.analyze_photo(photo_base64, analysis_prompt)
        
        await processing_msg.delete()
        
        if photo_result and not photo_result.get('error'):
            # Food analysis successful
            food_items = photo_result.get('food_items', [])
            reference_object = photo_result.get('reference_object', {})
            
            if food_items:
                result_text = get_text("food_analysis_title", user_language) + "\n\n"
                
                total_calories = 0
                total_proteins = 0
                total_fats = 0
                total_carbs = 0
                
                for item in food_items:
                    name = item.get('name', get_text("unknown_dish", user_language, default="Unknown dish"))
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
                    
                    confidence_text = {
                        Language.EN: f"confidence: {confidence*100:.0f}%",
                        Language.RU: f"уверенность: {confidence*100:.0f}%",
                        Language.UK: f"впевненість: {confidence*100:.0f}%"
                    }.get(user_language, f"confidence: {confidence*100:.0f}%")
                    
                    result_text += (
                        f"• <b>{name}</b>\n"
                        f"  ⚖️ ~{weight:.0f}г ({confidence_text})\n"
                        f"  " + get_text("nutrition_summary", user_language).format(
                            calories=calories, proteins=proteins, fats=fats, carbs=carbs
                        ).replace('\n', ' | ') + "\n\n"
                    )
                
                # Reference object info
                if reference_object.get('name'):
                    result_text += get_text("reference_object", user_language).format(
                        object=reference_object['name']
                    ) + "\n\n"
                
                # Total nutrition
                result_text += get_text("total_nutrition", user_language) + "\n"
                result_text += get_text("nutrition_summary", user_language).format(
                    calories=total_calories,
                    proteins=total_proteins,
                    fats=total_fats,
                    carbs=total_carbs
                ) + "\n\n"
                result_text += get_text("approximate_estimate", user_language)
                
                # Save to database
                user = await db_service.get_user_by_telegram_id(message.from_user.id)
                if user and food_items:
                    for item in food_items:
                        nutrition = item.get('nutrition_estimate', {})
                        await db_service.add_food_log(
                            user_id=user.id,
                            product_name=item.get('name', 'Photo dish'),
                            quantity_g=item.get('estimated_weight', 100),
                            calories=nutrition.get('calories', 0),
                            proteins=nutrition.get('proteins', 0),
                            fats=nutrition.get('fats', 0),
                            carbs=nutrition.get('carbs', 0),
                            source='photo'
                        )
                
                await message.answer(result_text, reply_markup=get_main_menu_keyboard(user_language))
            else:
                error_text = {
                    Language.EN: "❌ Could not recognize food in the photo.\n\nTry:\n• Take a clearer photo\n• Add reference object (coin, spoon)\n• Improve lighting",
                    Language.RU: "❌ Не удалось распознать еду на фото.\n\nПопробуйте:\n• Сделать фото более четким\n• Добавить эталонный объект (монета, ложка)\n• Улучшить освещение",
                    Language.UK: "❌ Не вдалося розпізнати їжу на фото.\n\nСпробуйте:\n• Зробити фото чіткішим\n• Додати еталонний об'єкт (монета, ложка)\n• Покращити освітлення"
                }.get(user_language, "❌ Could not recognize food in the photo.")
                
                await message.answer(error_text, reply_markup=get_main_menu_keyboard(user_language))
        else:
            # Both analyses failed
            error_msg = photo_result.get('error', 'Unknown error') if photo_result else 'Service unavailable'
            
            error_text = {
                Language.EN: f"❌ Could not process image.\n\nError: {error_msg}\n\nTry:\n• Take a new photo\n• Check image quality\n• Try again later",
                Language.RU: f"❌ Не удалось обработать изображение.\n\nОшибка: {error_msg}\n\nПопробуйте:\n• Сделать новое фото\n• Проверить качество изображения\n• Повторить попытку позже",
                Language.UK: f"❌ Не вдалося обробити зображення.\n\nПомилка: {error_msg}\n\nСпробуйте:\n• Зробити нове фото\n• Перевірити якість зображення\n• Повторити спробу пізніше"
            }.get(user_language, f"❌ Could not process image. Error: {error_msg}")
            
            await message.answer(error_text, reply_markup=get_main_menu_keyboard(user_language))
        
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await message.answer(
            get_text("error_processing_photo", user_language),
            reply_markup=get_main_menu_keyboard(user_language)
        )


def register_media_handlers(dp: Dispatcher) -> None:
    """Register media handlers"""
    dp.include_router(router)
