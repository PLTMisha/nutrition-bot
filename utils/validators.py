"""
Validation utilities for the Nutrition Bot
"""
import re
from typing import Optional, Tuple, List
from datetime import datetime, date


def validate_calories_goal(calories: int) -> bool:
    """Validate daily calorie goal"""
    return 800 <= calories <= 5000


def validate_telegram_id(telegram_id: int) -> bool:
    """Validate Telegram user ID"""
    return isinstance(telegram_id, int) and telegram_id > 0


def validate_username(username: Optional[str]) -> bool:
    """Validate Telegram username"""
    if username is None:
        return True
    
    # Username should be 5-32 characters, alphanumeric + underscores
    pattern = r'^[a-zA-Z0-9_]{5,32}$'
    return bool(re.match(pattern, username))


def validate_product_name(name: str) -> Tuple[bool, str]:
    """Validate product name"""
    if not name or not name.strip():
        return False, "Название продукта не может быть пустым"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Название продукта слишком короткое (минимум 2 символа)"
    
    if len(name) > 200:
        return False, "Название продукта слишком длинное (максимум 200 символов)"
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',
        r'eval\s*\(',
        r'exec\s*\(',
    ]
    
    name_lower = name.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, name_lower):
            return False, "Название содержит недопустимые символы"
    
    return True, "OK"


def validate_quantity(quantity: float) -> Tuple[bool, str]:
    """Validate food quantity"""
    if quantity <= 0:
        return False, "Количество должно быть больше нуля"
    
    if quantity > 10000:  # 10kg limit
        return False, "Количество слишком большое (максимум 10кг)"
    
    if quantity < 0.1:
        return False, "Количество слишком маленькое (минимум 0.1г)"
    
    return True, "OK"


def validate_nutrition_values(calories: float, proteins: float, fats: float, carbs: float) -> Tuple[bool, str]:
    """Validate nutrition values"""
    # Check for negative values
    if any(value < 0 for value in [calories, proteins, fats, carbs]):
        return False, "Значения БЖУ не могут быть отрицательными"
    
    # Check for unrealistic values (per 100g)
    if calories > 900:  # Pure fat has ~900 kcal/100g
        return False, "Слишком высокая калорийность"
    
    if proteins > 100:
        return False, "Слишком высокое содержание белков"
    
    if fats > 100:
        return False, "Слишком высокое содержание жиров"
    
    if carbs > 100:
        return False, "Слишком высокое содержание углеводов"
    
    # Check if macronutrients sum makes sense
    total_macros = proteins + fats + carbs
    if total_macros > 120:  # Allow some margin for fiber, water, etc.
        return False, "Сумма БЖУ превышает разумные пределы"
    
    # Rough calorie check (4 kcal/g for proteins/carbs, 9 kcal/g for fats)
    estimated_calories = proteins * 4 + carbs * 4 + fats * 9
    if abs(calories - estimated_calories) > calories * 0.5:  # 50% tolerance
        return False, "Калории не соответствуют содержанию БЖУ"
    
    return True, "OK"


def validate_barcode(barcode: str) -> Tuple[bool, str]:
    """Validate barcode format"""
    if not barcode or not barcode.strip():
        return False, "Штрих-код не может быть пустым"
    
    barcode = barcode.strip()
    
    # Check if it's all digits
    if not barcode.isdigit():
        return False, "Штрих-код должен содержать только цифры"
    
    # Check length (common barcode lengths)
    valid_lengths = [8, 12, 13, 14]  # EAN-8, UPC-A, EAN-13, ITF-14
    if len(barcode) not in valid_lengths:
        return False, f"Некорректная длина штрих-кода (должна быть {', '.join(map(str, valid_lengths))} цифр)"
    
    return True, "OK"


def validate_meal_type(meal_type: Optional[str]) -> bool:
    """Validate meal type"""
    if meal_type is None:
        return True
    
    valid_meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
    return meal_type in valid_meal_types


def validate_date_range(start_date: date, end_date: date) -> Tuple[bool, str]:
    """Validate date range"""
    if start_date > end_date:
        return False, "Начальная дата не может быть позже конечной"
    
    # Check if dates are not too far in the future
    today = date.today()
    if start_date > today:
        return False, "Начальная дата не может быть в будущем"
    
    if end_date > today:
        return False, "Конечная дата не может быть в будущем"
    
    # Check if range is not too large
    delta = end_date - start_date
    if delta.days > 365:
        return False, "Период не может превышать 365 дней"
    
    return True, "OK"


def validate_image_size(image_size: int, max_size: int = 10 * 1024 * 1024) -> Tuple[bool, str]:
    """Validate image file size"""
    if image_size <= 0:
        return False, "Некорректный размер изображения"
    
    if image_size > max_size:
        max_mb = max_size / (1024 * 1024)
        return False, f"Изображение слишком большое (максимум {max_mb:.1f}МБ)"
    
    return True, "OK"


def validate_image_format(file_extension: str) -> Tuple[bool, str]:
    """Validate image file format"""
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    
    if not file_extension:
        return False, "Не удалось определить формат файла"
    
    if file_extension.lower() not in valid_extensions:
        return False, f"Неподдерживаемый формат изображения. Поддерживаются: {', '.join(valid_extensions)}"
    
    return True, "OK"


def validate_user_input_length(text: str, max_length: int = 1000) -> Tuple[bool, str]:
    """Validate user input length"""
    if len(text) > max_length:
        return False, f"Текст слишком длинный (максимум {max_length} символов)"
    
    return True, "OK"


def validate_search_query(query: str) -> Tuple[bool, str]:
    """Validate search query"""
    if not query or not query.strip():
        return False, "Поисковый запрос не может быть пустым"
    
    query = query.strip()
    
    if len(query) < 2:
        return False, "Поисковый запрос слишком короткий (минимум 2 символа)"
    
    if len(query) > 100:
        return False, "Поисковый запрос слишком длинный (максимум 100 символов)"
    
    # Check for suspicious patterns
    if re.search(r'[<>"\']', query):
        return False, "Поисковый запрос содержит недопустимые символы"
    
    return True, "OK"


def validate_confidence_score(score: float) -> bool:
    """Validate confidence score (0.0 to 1.0)"""
    return 0.0 <= score <= 1.0


def validate_age(age: int) -> Tuple[bool, str]:
    """Validate user age"""
    if age < 10:
        return False, "Возраст не может быть меньше 10 лет"
    
    if age > 120:
        return False, "Возраст не может быть больше 120 лет"
    
    return True, "OK"


def validate_weight(weight: float) -> Tuple[bool, str]:
    """Validate user weight in kg"""
    if weight < 20:
        return False, "Вес не может быть меньше 20 кг"
    
    if weight > 500:
        return False, "Вес не может быть больше 500 кг"
    
    return True, "OK"


def validate_height(height: float) -> Tuple[bool, str]:
    """Validate user height in cm"""
    if height < 100:
        return False, "Рост не может быть меньше 100 см"
    
    if height > 250:
        return False, "Рост не может быть больше 250 см"
    
    return True, "OK"


def validate_activity_level(activity_level: str) -> bool:
    """Validate activity level"""
    valid_levels = ['sedentary', 'light', 'moderate', 'active', 'very_active']
    return activity_level in valid_levels


def validate_gender(gender: str) -> bool:
    """Validate gender"""
    valid_genders = ['male', 'female']
    return gender.lower() in valid_genders


def sanitize_user_input(text: str) -> str:
    """Sanitize user input to prevent XSS and other attacks"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove script-related content
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def validate_callback_data(callback_data: str) -> Tuple[bool, str]:
    """Validate callback data format"""
    if not callback_data:
        return False, "Callback data не может быть пустым"
    
    if len(callback_data) > 64:  # Telegram limit
        return False, "Callback data слишком длинный"
    
    # Check for valid characters (alphanumeric, underscore, dash)
    if not re.match(r'^[a-zA-Z0-9_\-]+$', callback_data):
        return False, "Callback data содержит недопустимые символы"
    
    return True, "OK"


def validate_language_code(lang_code: str) -> bool:
    """Validate language code"""
    # ISO 639-1 language codes
    valid_codes = ['en', 'ru', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko']
    return lang_code.lower() in valid_codes


def validate_timezone(timezone: str) -> bool:
    """Validate timezone string"""
    # Basic validation for common timezone formats
    timezone_patterns = [
        r'^UTC[+-]\d{1,2}$',  # UTC+3, UTC-5
        r'^[A-Z]{3,4}$',      # MSK, EST, PST
        r'^[A-Za-z_/]+$',     # Europe/Moscow, America/New_York
    ]
    
    return any(re.match(pattern, timezone) for pattern in timezone_patterns)


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_and_raise(validator_func, value, error_message: str = None):
    """Validate value and raise ValidationError if invalid"""
    if hasattr(validator_func, '__call__'):
        if validator_func.__code__.co_argcount == 1:
            # Single argument validator
            result = validator_func(value)
            if isinstance(result, tuple):
                is_valid, message = result
                if not is_valid:
                    raise ValidationError(error_message or message)
            elif not result:
                raise ValidationError(error_message or "Validation failed")
        else:
            # Multiple argument validator - not supported in this helper
            raise ValueError("Multi-argument validators not supported")


def validate_nutrition_data(data: dict) -> List[str]:
    """Validate complete nutrition data and return list of errors"""
    errors = []
    
    # Required fields
    required_fields = ['name', 'calories_per_100g', 'proteins_per_100g', 'fats_per_100g', 'carbs_per_100g']
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"Отсутствует обязательное поле: {field}")
    
    # Validate product name
    if 'name' in data:
        is_valid, message = validate_product_name(data['name'])
        if not is_valid:
            errors.append(f"Название продукта: {message}")
    
    # Validate nutrition values
    if all(field in data for field in ['calories_per_100g', 'proteins_per_100g', 'fats_per_100g', 'carbs_per_100g']):
        is_valid, message = validate_nutrition_values(
            data['calories_per_100g'],
            data['proteins_per_100g'],
            data['fats_per_100g'],
            data['carbs_per_100g']
        )
        if not is_valid:
            errors.append(f"Питательная ценность: {message}")
    
    # Validate barcode if present
    if 'barcode' in data and data['barcode']:
        is_valid, message = validate_barcode(data['barcode'])
        if not is_valid:
            errors.append(f"Штрих-код: {message}")
    
    return errors
