"""
Helper functions for the Nutrition Bot
"""
import re
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO

from utils.i18n import get_text, Language

logger = logging.getLogger(__name__)


def format_nutrition_summary(nutrition_data: Dict[str, float], language: Language = Language.EN) -> str:
    """Format nutrition data for display"""
    calories = nutrition_data.get('calories', 0)
    proteins = nutrition_data.get('proteins', 0)
    fats = nutrition_data.get('fats', 0)
    carbs = nutrition_data.get('carbs', 0)
    
    return get_text("nutrition_summary", language).format(
        calories=calories,
        proteins=proteins,
        fats=fats,
        carbs=carbs
    )


def format_user_stats(user, today_stats: Dict[str, float], week_stats: Dict[str, float], language: Language = Language.EN) -> str:
    """Format user statistics for display"""
    today_calories = today_stats.get('calories', 0)
    today_entries = today_stats.get('entries_count', 0)
    
    week_calories = week_stats.get('calories', 0)
    week_entries = week_stats.get('entries_count', 0)
    week_days = week_stats.get('days', 7)
    
    # Calculate progress towards daily goal
    goal_calories = user.daily_goal_calories
    progress_percent = (today_calories / goal_calories * 100) if goal_calories > 0 else 0
    remaining_calories = max(0, goal_calories - today_calories)
    
    # Progress bar
    progress_bar = create_progress_bar(progress_percent)
    
    # Average daily calories for the week
    avg_daily_calories = week_calories / week_days if week_days > 0 else 0
    
    stats_text = get_text("stats_message", language).format(
        name=user.display_name,
        goal_calories=goal_calories,
        progress_bar=progress_bar,
        progress_percent=progress_percent,
        today_calories=today_calories,
        today_entries=today_entries,
        remaining_calories=remaining_calories,
        week_calories=week_calories,
        avg_daily_calories=avg_daily_calories,
        week_entries=week_entries,
        nutrition_summary=format_nutrition_summary(today_stats, language)
    )
    
    return stats_text.strip()


def create_progress_bar(percent: float, length: int = 10) -> str:
    """Create a visual progress bar"""
    filled = int(percent / 100 * length)
    bar = "🟩" * filled + "⬜" * (length - filled)
    return bar


def parse_food_query(text: str) -> Tuple[Optional[str], Optional[float]]:
    """Parse food query to extract product name and quantity"""
    # Remove common words and normalize
    text = text.strip().lower()
    
    # Patterns to match quantity
    quantity_patterns = [
        r'(\d+(?:\.\d+)?)\s*г(?:рамм)?',  # 100г, 100 грамм
        r'(\d+(?:\.\d+)?)\s*мл',          # 200мл
        r'(\d+(?:\.\d+)?)\s*шт',          # 1шт
        r'(\d+(?:\.\d+)?)\s*штук',        # 2 штуки
        r'(\d+(?:\.\d+)?)\s*кг',          # 0.5кг
        r'(\d+(?:\.\d+)?)\s*л',           # 1л
        r'(\d+(?:\.\d+)?)\s*стакан',      # 1 стакан
        r'(\d+(?:\.\d+)?)\s*ложк',        # 2 ложки
        r'(\d+(?:\.\d+)?)\s*чашк',        # 1 чашка
        r'(\d+(?:\.\d+)?)\s*порци',       # 1 порция
    ]
    
    quantity = None
    product_name = text
    
    # Try to find quantity
    for pattern in quantity_patterns:
        match = re.search(pattern, text)
        if match:
            quantity = float(match.group(1))
            
            # Convert units to grams
            if 'кг' in match.group(0):
                quantity *= 1000
            elif 'л' in match.group(0):
                quantity *= 1000  # Assume 1л = 1000г for liquids
            elif 'стакан' in match.group(0):
                quantity *= 200   # Standard glass ~200ml
            elif 'ложк' in match.group(0):
                quantity *= 15    # Tablespoon ~15г
            elif 'чашк' in match.group(0):
                quantity *= 250   # Cup ~250ml
            elif 'порци' in match.group(0):
                quantity *= 100   # Average portion ~100г
            elif 'шт' in match.group(0):
                quantity *= 100   # Default weight per piece
            
            # Remove quantity from product name
            product_name = re.sub(pattern, '', text).strip()
            break
    
    # Clean up product name
    product_name = re.sub(r'\s+', ' ', product_name).strip()
    
    # Remove common prefixes/suffixes
    cleanup_words = ['найти', 'поиск', 'добавить', 'сколько', 'в', 'на', 'из', 'для']
    words = product_name.split()
    words = [word for word in words if word not in cleanup_words]
    product_name = ' '.join(words)
    
    if not product_name:
        return None, quantity
    
    return product_name, quantity


def format_product_info(product: Dict[str, Any], quantity: float = 100) -> str:
    """Format product information for display"""
    name = product.get('name', 'Unknown Product')
    brand = product.get('brand', '')
    
    # Nutrition per specified quantity
    multiplier = quantity / 100.0
    calories = product.get('calories_per_100g', 0) * multiplier
    proteins = product.get('proteins_per_100g', 0) * multiplier
    fats = product.get('fats_per_100g', 0) * multiplier
    carbs = product.get('carbs_per_100g', 0) * multiplier
    
    # Additional nutrition if available
    fiber = product.get('fiber_per_100g')
    sugar = product.get('sugar_per_100g')
    sodium = product.get('sodium_per_100g')
    
    info_text = f"🍽️ <b>{name}</b>\n"
    
    if brand:
        info_text += f"🏷️ <b>Бренд:</b> {brand}\n"
    
    info_text += f"⚖️ <b>Количество:</b> {quantity}г\n\n"
    info_text += format_nutrition_summary({
        'calories': calories,
        'proteins': proteins,
        'fats': fats,
        'carbs': carbs
    })
    
    # Add additional nutrition if available
    additional_info = []
    if fiber is not None:
        additional_info.append(f"🌾 Клетчатка: {fiber * multiplier:.1f}г")
    if sugar is not None:
        additional_info.append(f"🍯 Сахар: {sugar * multiplier:.1f}г")
    if sodium is not None:
        additional_info.append(f"🧂 Натрий: {sodium * multiplier:.1f}мг")
    
    if additional_info:
        info_text += "\n\n" + "\n".join(additional_info)
    
    return info_text


def calculate_daily_progress(current: float, goal: float) -> Dict[str, Any]:
    """Calculate daily progress statistics"""
    if goal <= 0:
        return {
            'percent': 0,
            'remaining': 0,
            'status': 'no_goal',
            'message': 'Цель не установлена'
        }
    
    percent = (current / goal) * 100
    remaining = goal - current
    
    if percent < 50:
        status = 'low'
        message = f'Осталось {remaining:.0f} ккал до цели'
    elif percent < 90:
        status = 'good'
        message = f'Хороший прогресс! Осталось {remaining:.0f} ккал'
    elif percent <= 110:
        status = 'excellent'
        message = 'Отличный результат! Цель достигнута'
    else:
        status = 'over'
        message = f'Превышение на {abs(remaining):.0f} ккал'
    
    return {
        'percent': percent,
        'remaining': remaining,
        'status': status,
        'message': message
    }


def generate_nutrition_chart(data: List[Dict[str, Any]], period: str = 'week') -> BytesIO:
    """Generate nutrition chart"""
    try:
        # Set up the plot
        plt.style.use('default')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.suptitle(f'Статистика питания за {period}', fontsize=16, fontweight='bold')
        
        # Extract data
        dates = [item['date'] for item in data]
        calories = [item['calories'] for item in data]
        proteins = [item['proteins'] for item in data]
        fats = [item['fats'] for item in data]
        carbs = [item['carbs'] for item in data]
        
        # Plot calories
        ax1.plot(dates, calories, marker='o', linewidth=2, markersize=6, color='#FF6B6B')
        ax1.set_title('Калории', fontweight='bold')
        ax1.set_ylabel('ккал')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Plot macronutrients
        ax2.plot(dates, proteins, marker='s', label='Белки', linewidth=2, color='#4ECDC4')
        ax2.plot(dates, fats, marker='^', label='Жиры', linewidth=2, color='#45B7D1')
        ax2.plot(dates, carbs, marker='D', label='Углеводы', linewidth=2, color='#96CEB4')
        
        ax2.set_title('Макронутриенты', fontweight='bold')
        ax2.set_ylabel('граммы')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # Format dates on x-axis
        if len(dates) > 0:
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        
        plt.tight_layout()
        
        # Save to BytesIO
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        return buffer
        
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        return None


def format_barcode_result(barcode_data: Dict[str, Any]) -> str:
    """Format barcode scan result for display"""
    barcode = barcode_data.get('barcode', 'Unknown')
    found_in_db = barcode_data.get('found_in_database', False)
    
    result_text = f"📱 <b>Штрих-код:</b> {barcode}\n\n"
    
    if found_in_db and 'product' in barcode_data:
        product = barcode_data['product']
        result_text += format_product_info(product, 100)
        result_text += "\n\n💡 <i>Укажите количество для расчета БЖУ</i>"
    else:
        result_text += (
            "❌ <b>Продукт не найден в базе данных</b>\n\n"
            "Попробуйте:\n"
            "• Поиск по названию\n"
            "• Сканирование другого кода\n"
            "• Ручной ввод данных"
        )
    
    return result_text


def format_time_ago(dt: datetime) -> str:
    """Format time difference in human-readable format"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} дн. назад"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} ч. назад"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} мин. назад"
    else:
        return "только что"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def clean_product_name(name: str) -> str:
    """Clean and normalize product name"""
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name.strip())
    
    # Remove special characters but keep letters, numbers, and basic punctuation
    name = re.sub(r'[^\w\s\-\.,]', '', name)
    
    # Capitalize first letter
    name = name.capitalize()
    
    return name


def validate_quantity(quantity_str: str) -> Tuple[bool, Optional[float], str]:
    """Validate and parse quantity input"""
    try:
        # Remove common suffixes
        quantity_str = re.sub(r'[^\d\.]', '', quantity_str.strip())
        
        if not quantity_str:
            return False, None, "Количество не указано"
        
        quantity = float(quantity_str)
        
        if quantity <= 0:
            return False, None, "Количество должно быть больше нуля"
        
        if quantity > 5000:  # 5kg limit
            return False, None, "Количество слишком большое (максимум 5000г)"
        
        return True, quantity, "OK"
        
    except ValueError:
        return False, None, "Некорректный формат количества"


def format_meal_type(meal_type: Optional[str]) -> str:
    """Format meal type for display"""
    meal_types = {
        'breakfast': '🌅 Завтрак',
        'lunch': '🌞 Обед',
        'dinner': '🌆 Ужин',
        'snack': '🍿 Перекус'
    }
    return meal_types.get(meal_type, '🍽️ Прием пищи')


def calculate_bmi(weight_kg: float, height_cm: float) -> Tuple[float, str]:
    """Calculate BMI and category"""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Недостаточный вес"
    elif bmi < 25:
        category = "Нормальный вес"
    elif bmi < 30:
        category = "Избыточный вес"
    else:
        category = "Ожирение"
    
    return round(bmi, 1), category


def estimate_daily_calories(weight_kg: float, height_cm: float, age: int, gender: str, activity_level: str) -> int:
    """Estimate daily calorie needs using Mifflin-St Jeor equation"""
    # Base metabolic rate
    if gender.lower() == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    # Activity multipliers
    activity_multipliers = {
        'sedentary': 1.2,      # Little/no exercise
        'light': 1.375,        # Light exercise 1-3 days/week
        'moderate': 1.55,      # Moderate exercise 3-5 days/week
        'active': 1.725,       # Heavy exercise 6-7 days/week
        'very_active': 1.9     # Very heavy exercise, physical job
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.55)
    daily_calories = bmr * multiplier
    
    return int(daily_calories)


def generate_meal_suggestions(target_calories: int, meal_type: str) -> List[str]:
    """Generate meal suggestions based on target calories and meal type"""
    suggestions = {
        'breakfast': [
            "Овсянка с фруктами и орехами",
            "Яичница с овощами и хлебом",
            "Творог с ягодами и медом",
            "Смузи с бананом и протеином",
            "Мюсли с молоком и фруктами"
        ],
        'lunch': [
            "Куриная грудка с рисом и овощами",
            "Рыба с картофелем и салатом",
            "Паста с томатным соусом и сыром",
            "Суп с мясом и хлебом",
            "Салат с курицей и авокадо"
        ],
        'dinner': [
            "Запеченная рыба с овощами",
            "Куриное филе с салатом",
            "Омлет с овощами",
            "Творожная запеканка",
            "Легкий суп с зеленью"
        ],
        'snack': [
            "Яблоко с орехами",
            "Йогурт с ягодами",
            "Морковь с хумусом",
            "Протеиновый батончик",
            "Горсть орехов"
        ]
    }
    
    return suggestions.get(meal_type, suggestions['snack'])


def format_error_message(error_type: str, details: str = "") -> str:
    """Format error messages for users"""
    error_messages = {
        'network': "🌐 Проблемы с сетью. Попробуйте позже.",
        'api_limit': "⏰ Превышен лимит запросов. Попробуйте через несколько минут.",
        'invalid_image': "📷 Некорректное изображение. Попробуйте другое фото.",
        'no_barcode': "📱 Штрих-код не найден на изображении.",
        'product_not_found': "🔍 Продукт не найден в базе данных.",
        'invalid_quantity': "⚖️ Некорректное количество. Укажите число больше нуля.",
        'database_error': "💾 Ошибка базы данных. Попробуйте позже.",
        'general': "❌ Произошла ошибка. Попробуйте еще раз."
    }
    
    message = error_messages.get(error_type, error_messages['general'])
    
    if details:
        message += f"\n\n<i>Детали: {details}</i>"
    
    return message
