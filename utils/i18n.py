"""
Internationalization (i18n) support for the Nutrition Bot
"""
import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages"""
    EN = "en"
    RU = "ru"
    UK = "uk"


class I18n:
    """Internationalization manager"""
    
    def __init__(self):
        self.translations = self._load_translations()
        self.default_language = Language.EN
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load all translations"""
        return {
            # Basic commands and navigation
            "welcome_title": {
                "en": "🍎 <b>Welcome to Nutrition Bot!</b>",
                "ru": "🍎 <b>Добро пожаловать в Nutrition Bot!</b>",
                "uk": "🍎 <b>Ласкаво просимо до Nutrition Bot!</b>"
            },
            "welcome_greeting": {
                "en": "Hello, {name}! 👋",
                "ru": "Привет, {name}! 👋",
                "uk": "Привіт, {name}! 👋"
            },
            "welcome_description": {
                "en": "I'll help you track calories and macronutrients. Here's what I can do:",
                "ru": "Я помогу тебе отслеживать калории и БЖУ. Вот что я умею:",
                "uk": "Я допоможу тобі відстежувати калорії та БЖУ. Ось що я вмію:"
            },
            "feature_search": {
                "en": "🔍 <b>Product Search</b>\nJust type product name and quantity in grams",
                "ru": "🔍 <b>Поиск продуктов</b>\nПросто напиши название продукта и количество граммов",
                "uk": "🔍 <b>Пошук продуктів</b>\nПросто напиши назву продукту та кількість грамів"
            },
            "feature_barcode": {
                "en": "📷 <b>Barcode Scanning</b>\nSend a photo of product barcode",
                "ru": "📷 <b>Сканирование штрих-кодов</b>\nОтправь фото штрих-кода товара",
                "uk": "📷 <b>Сканування штрих-кодів</b>\nНадішли фото штрих-коду товару"
            },
            "feature_photo": {
                "en": "🍽️ <b>Food Photo Analysis</b>\nTake a photo of your meal with a reference object (coin, spoon, plate)",
                "ru": "🍽️ <b>Анализ блюд по фото</b>\nСфотографируй блюдо с эталонным предметом (монета, ложка, тарелка)",
                "uk": "🍽️ <b>Аналіз страв за фото</b>\nСфотографуй страву з еталонним предметом (монета, ложка, тарілка)"
            },
            "feature_stats": {
                "en": "📊 <b>Statistics and Goals</b>\nTrack progress and set daily goals",
                "ru": "📊 <b>Статистика и цели</b>\nОтслеживай прогресс и устанавливай дневные цели",
                "uk": "📊 <b>Статистика та цілі</b>\nВідстежуй прогрес та встановлюй денні цілі"
            },
            "current_goal": {
                "en": "<b>Your current goal:</b> {calories} kcal/day",
                "ru": "<b>Твоя текущая цель:</b> {calories} ккал/день",
                "uk": "<b>Твоя поточна ціль:</b> {calories} ккал/день"
            },
            "choose_action": {
                "en": "Choose an action from the menu below or just type a product name! 👇",
                "ru": "Выбери действие из меню ниже или просто напиши название продукта! 👇",
                "uk": "Обери дію з меню нижче або просто напиши назву продукту! 👇"
            },
            
            # Help command
            "help_title": {
                "en": "🆘 <b>Command Help</b>",
                "ru": "🆘 <b>Справка по командам</b>",
                "uk": "🆘 <b>Довідка по командах</b>"
            },
            "help_basic_commands": {
                "en": "<b>Basic Commands:</b>",
                "ru": "<b>Основные команды:</b>",
                "uk": "<b>Основні команди:</b>"
            },
            "help_cmd_start": {
                "en": "/start - Start bot and register",
                "ru": "/start - Запуск бота и регистрация",
                "uk": "/start - Запуск бота та реєстрація"
            },
            "help_cmd_help": {
                "en": "/help - Show this help",
                "ru": "/help - Показать эту справку",
                "uk": "/help - Показати цю довідку"
            },
            "help_cmd_stats": {
                "en": "/stats - Statistics for day/week/month",
                "ru": "/stats - Статистика за день/неделю/месяц",
                "uk": "/stats - Статистика за день/тиждень/місяць"
            },
            "help_cmd_goal": {
                "en": "/goal - Set daily calorie goal",
                "ru": "/goal - Установить дневную цель калорий",
                "uk": "/goal - Встановити денну ціль калорій"
            },
            "help_cmd_history": {
                "en": "/history - Recent food entries",
                "ru": "/history - Последние записи питания",
                "uk": "/history - Останні записи харчування"
            },
            "help_cmd_clear": {
                "en": "/clear - Clear today's data",
                "ru": "/clear - Очистить данные за сегодня",
                "uk": "/clear - Очистити дані за сьогодні"
            },
            "help_cmd_lang": {
                "en": "/lang - Change language",
                "ru": "/lang - Изменить язык",
                "uk": "/lang - Змінити мову"
            },
            
            # Product search
            "product_not_recognized": {
                "en": "❌ Could not recognize the product.\n\nTry writing like this:\n• apple 150g\n• bread 50g\n• milk 200ml",
                "ru": "❌ Не удалось распознать продукт.\n\nПопробуйте написать так:\n• яблоко 150г\n• хлеб 50г\n• молоко 200мл",
                "uk": "❌ Не вдалося розпізнати продукт.\n\nСпробуйте написати так:\n• яблуко 150г\n• хліб 50г\n• молоко 200мл"
            },
            "product_not_found": {
                "en": "❌ Product '{product}' not found.\n\nTry:\n• Change the name\n• Use English name\n• Scan barcode",
                "ru": "❌ Продукт '{product}' не найден.\n\nПопробуйте:\n• Изменить название\n• Использовать английское название\n• Сфотографировать штрих-код",
                "uk": "❌ Продукт '{product}' не знайдено.\n\nСпробуйте:\n• Змінити назву\n• Використати англійську назву\n• Сфотографувати штрих-код"
            },
            "product_added": {
                "en": "✅ <b>Product added!</b>",
                "ru": "✅ <b>Продукт добавлен!</b>",
                "uk": "✅ <b>Продукт додано!</b>"
            },
            
            # Statistics
            "stats_title": {
                "en": "📊 <b>Nutrition Statistics</b>",
                "ru": "📊 <b>Статистика питания</b>",
                "uk": "📊 <b>Статистика харчування</b>"
            },
            "stats_user": {
                "en": "👤 <b>User:</b> {name}",
                "ru": "👤 <b>Пользователь:</b> {name}",
                "uk": "👤 <b>Користувач:</b> {name}"
            },
            "stats_daily_goal": {
                "en": "🎯 <b>Daily Goal:</b> {calories} kcal",
                "ru": "🎯 <b>Дневная цель:</b> {calories} ккал",
                "uk": "🎯 <b>Денна ціль:</b> {calories} ккал"
            },
            "stats_today": {
                "en": "📅 <b>Today:</b>",
                "ru": "📅 <b>Сегодня:</b>",
                "uk": "📅 <b>Сьогодні:</b>"
            },
            "stats_consumed": {
                "en": "🔥 Consumed: <b>{calories} kcal</b>",
                "ru": "🔥 Потреблено: <b>{calories} ккал</b>",
                "uk": "🔥 Спожито: <b>{calories} ккал</b>"
            },
            "stats_entries": {
                "en": "📝 Entries: {count}",
                "ru": "📝 Записей: {count}",
                "uk": "📝 Записів: {count}"
            },
            "stats_remaining": {
                "en": "⚖️ Remaining: {calories} kcal",
                "ru": "⚖️ Осталось: {calories} ккал",
                "uk": "⚖️ Залишилось: {calories} ккал"
            },
            "stats_week": {
                "en": "📊 <b>This Week:</b>",
                "ru": "📊 <b>За неделю:</b>",
                "uk": "📊 <b>За тиждень:</b>"
            },
            "stats_total": {
                "en": "🔥 Total: {calories} kcal",
                "ru": "🔥 Всего: {calories} ккал",
                "uk": "🔥 Всього: {calories} ккал"
            },
            "stats_average": {
                "en": "📈 Average per day: {calories} kcal",
                "ru": "📈 В среднем в день: {calories} ккал",
                "uk": "📈 В середньому на день: {calories} ккал"
            },
            
            # Nutrition info
            "calories": {
                "en": "🔥 <b>{calories} kcal</b>",
                "ru": "🔥 <b>{calories} ккал</b>",
                "uk": "🔥 <b>{calories} ккал</b>"
            },
            "proteins": {
                "en": "🥩 Proteins: {proteins}g",
                "ru": "🥩 Белки: {proteins}г",
                "uk": "🥩 Білки: {proteins}г"
            },
            "fats": {
                "en": "🧈 Fats: {fats}g",
                "ru": "🧈 Жиры: {fats}г",
                "uk": "🧈 Жири: {fats}г"
            },
            "carbs": {
                "en": "🍞 Carbs: {carbs}g",
                "ru": "🍞 Углеводы: {carbs}г",
                "uk": "🍞 Вуглеводи: {carbs}г"
            },
            
            # Buttons
            "btn_main_menu": {
                "en": "🏠 Main Menu",
                "ru": "🏠 Главное меню",
                "uk": "🏠 Головне меню"
            },
            "btn_search": {
                "en": "🔍 Search Products",
                "ru": "🔍 Поиск продуктов",
                "uk": "🔍 Пошук продуктів"
            },
            "btn_scan_barcode": {
                "en": "📱 Scan Barcode",
                "ru": "📱 Сканировать код",
                "uk": "📱 Сканувати код"
            },
            "btn_photo_analysis": {
                "en": "📷 Photo Analysis",
                "ru": "📷 Анализ фото",
                "uk": "📷 Аналіз фото"
            },
            "btn_statistics": {
                "en": "📊 Statistics",
                "ru": "📊 Статистика",
                "uk": "📊 Статистика"
            },
            "btn_settings": {
                "en": "⚙️ Settings",
                "ru": "⚙️ Настройки",
                "uk": "⚙️ Налаштування"
            },
            "btn_language": {
                "en": "🌐 Language",
                "ru": "🌐 Язык",
                "uk": "🌐 Мова"
            },
            "btn_history": {
                "en": "📝 History",
                "ru": "📝 История",
                "uk": "📝 Історія"
            },
            "btn_export": {
                "en": "📤 Export Data",
                "ru": "📤 Экспорт данных",
                "uk": "📤 Експорт даних"
            },
            "btn_weekly_chart": {
                "en": "📈 Weekly Chart",
                "ru": "📈 График за неделю",
                "uk": "📈 Графік за тиждень"
            },
            "btn_monthly_chart": {
                "en": "📊 Monthly Chart",
                "ru": "📊 График за месяц",
                "uk": "📊 Графік за місяць"
            },
            
            # Language selection
            "select_language": {
                "en": "🌐 <b>Select Language</b>\n\nChoose your preferred language:",
                "ru": "🌐 <b>Выбор языка</b>\n\nВыберите предпочитаемый язык:",
                "uk": "🌐 <b>Вибір мови</b>\n\nОберіть бажану мову:"
            },
            "language_changed": {
                "en": "✅ Language changed to English",
                "ru": "✅ Язык изменен на русский",
                "uk": "✅ Мову змінено на українську"
            },
            
            # Errors
            "error_general": {
                "en": "❌ An error occurred. Please try again.",
                "ru": "❌ Произошла ошибка. Попробуйте еще раз.",
                "uk": "❌ Сталася помилка. Спробуйте ще раз."
            },
            "error_user_not_found": {
                "en": "❌ User not found. Use /start",
                "ru": "❌ Пользователь не найден. Используйте /start",
                "uk": "❌ Користувача не знайдено. Використайте /start"
            },
            "error_processing_photo": {
                "en": "❌ Error processing photo",
                "ru": "❌ Ошибка при обработке фото",
                "uk": "❌ Помилка при обробці фото"
            },
            "error_search": {
                "en": "❌ Error searching for product",
                "ru": "❌ Ошибка при поиске продукта",
                "uk": "❌ Помилка при пошуку продукту"
            },
            
            # Photo processing
            "processing_image": {
                "en": "🔄 Processing image...",
                "ru": "🔄 Обрабатываю изображение...",
                "uk": "🔄 Обробляю зображення..."
            },
            "barcode_detected": {
                "en": "📱 <b>Barcode:</b> {barcode}",
                "ru": "📱 <b>Штрих-код:</b> {barcode}",
                "uk": "📱 <b>Штрих-код:</b> {barcode}"
            },
            "product_found_db": {
                "en": "✅ Product found in database",
                "ru": "✅ Продукт найден в базе данных",
                "uk": "✅ Продукт знайдено в базі даних"
            },
            "product_not_found_db": {
                "en": "❌ <b>Product not found in database</b>\n\nTry:\n• Search by name\n• Scan different barcode\n• Manual entry",
                "ru": "❌ <b>Продукт не найден в базе данных</b>\n\nПопробуйте:\n• Поиск по названию\n• Сканирование другого кода\n• Ручной ввод данных",
                "uk": "❌ <b>Продукт не знайдено в базі даних</b>\n\nСпробуйте:\n• Пошук за назвою\n• Сканування іншого коду\n• Ручне введення даних"
            },
            "specify_quantity": {
                "en": "💡 Specify quantity in grams to add to food diary",
                "ru": "💡 Укажите количество в граммах для добавления в дневник питания",
                "uk": "💡 Вкажіть кількість у грамах для додавання до щоденника харчування"
            },
            
            # Food analysis
            "food_analysis_title": {
                "en": "🍽️ <b>Food Analysis:</b>",
                "ru": "🍽️ <b>Анализ блюда:</b>",
                "uk": "🍽️ <b>Аналіз страви:</b>"
            },
            "reference_object": {
                "en": "📏 <b>Reference object:</b> {object}",
                "ru": "📏 <b>Эталонный объект:</b> {object}",
                "uk": "📏 <b>Еталонний об'єкт:</b> {object}"
            },
            "total_nutrition": {
                "en": "📊 <b>Total:</b>",
                "ru": "📊 <b>Итого:</b>",
                "uk": "📊 <b>Разом:</b>"
            },
            "approximate_estimate": {
                "en": "💡 <i>This is an approximate estimate. You can adjust the data.</i>",
                "ru": "💡 <i>Это приблизительная оценка. Вы можете скорректировать данные.</i>",
                "uk": "💡 <i>Це приблизна оцінка. Ви можете скоригувати дані.</i>"
            },
            
            # Goal setting
            "goal_usage": {
                "en": "📊 <b>Setting Daily Goal</b>\n\nUse: <code>/goal 2000</code>\nWhere 2000 is desired calories per day\n\nRecommended values:\n• Women: 1800-2200 kcal\n• Men: 2200-2800 kcal",
                "ru": "📊 <b>Установка дневной цели</b>\n\nИспользуйте: <code>/goal 2000</code>\nГде 2000 - желаемое количество калорий в день\n\nРекомендуемые значения:\n• Женщины: 1800-2200 ккал\n• Мужчины: 2200-2800 ккал",
                "uk": "📊 <b>Встановлення денної цілі</b>\n\nВикористовуйте: <code>/goal 2000</code>\nДе 2000 - бажана кількість калорій на день\n\nРекомендовані значення:\n• Жінки: 1800-2200 ккал\n• Чоловіки: 2200-2800 ккал"
            },
            "goal_invalid": {
                "en": "❌ Invalid goal. Specify value between 800 and 5000 kcal",
                "ru": "❌ Некорректная цель. Укажите значение от 800 до 5000 ккал",
                "uk": "❌ Некоректна ціль. Вкажіть значення від 800 до 5000 ккал"
            },
            "goal_invalid_number": {
                "en": "❌ Please specify a valid number of calories",
                "ru": "❌ Укажите корректное число калорий",
                "uk": "❌ Вкажіть коректне число калорій"
            },
            "goal_updated": {
                "en": "✅ <b>Goal updated!</b>\n\nYour new daily goal: <b>{calories} kcal</b>\nGood luck achieving your goal! 💪",
                "ru": "✅ <b>Цель обновлена!</b>\n\nВаша новая дневная цель: <b>{calories} ккал</b>\nУдачи в достижении цели! 💪",
                "uk": "✅ <b>Ціль оновлено!</b>\n\nВаша нова денна ціль: <b>{calories} ккал</b>\nУдачі в досягненні цілі! 💪"
            },
            
            # History
            "history_title": {
                "en": "📝 <b>Food History</b>",
                "ru": "📝 <b>История питания</b>",
                "uk": "📝 <b>Історія харчування</b>"
            },
            "history_empty": {
                "en": "📝 <b>Food History</b>\n\nYou don't have any entries yet.\nAdd your first product! 🍎",
                "ru": "📝 <b>История питания</b>\n\nУ вас пока нет записей.\nДобавьте первый продукт! 🍎",
                "uk": "📝 <b>Історія харчування</b>\n\nУ вас поки немає записів.\nДодайте перший продукт! 🍎"
            },
            "recent_entries": {
                "en": "📝 <b>Recent entries:</b>",
                "ru": "📝 <b>Последние записи:</b>",
                "uk": "📝 <b>Останні записи:</b>"
            },
            
            # Combined messages used in handlers
            "welcome_message": {
                "en": """🍎 <b>Welcome to Nutrition Bot!</b>

Hello, {name}! 👋

I'll help you track calories and macronutrients. Here's what I can do:

🔍 <b>Product Search</b>
Just type product name and quantity in grams

📷 <b>Barcode Scanning</b>
Send a photo of product barcode

🍽️ <b>Food Photo Analysis</b>
Take a photo of your meal with a reference object (coin, spoon, plate)

📊 <b>Statistics and Goals</b>
Track progress and set daily goals

<b>Your current goal:</b> {daily_goal} kcal/day

Choose an action from the menu below or just type a product name! 👇""",
                "ru": """🍎 <b>Добро пожаловать в Nutrition Bot!</b>

Привет, {name}! 👋

Я помогу тебе отслеживать калории и БЖУ. Вот что я умею:

🔍 <b>Поиск продуктов</b>
Просто напиши название продукта и количество граммов

📷 <b>Сканирование штрих-кодов</b>
Отправь фото штрих-кода товара

🍽️ <b>Анализ блюд по фото</b>
Сфотографируй блюдо с эталонным предметом (монета, ложка, тарелка)

📊 <b>Статистика и цели</b>
Отслеживай прогресс и устанавливай дневные цели

<b>Твоя текущая цель:</b> {daily_goal} ккал/день

Выбери действие из меню ниже или просто напиши название продукта! 👇""",
                "uk": """🍎 <b>Ласкаво просимо до Nutrition Bot!</b>

Привіт, {name}! 👋

Я допоможу тобі відстежувати калорії та БЖУ. Ось що я вмію:

🔍 <b>Пошук продуктів</b>
Просто напиши назву продукту та кількість грамів

📷 <b>Сканування штрих-кодів</b>
Надішли фото штрих-коду товару

🍽️ <b>Аналіз страв за фото</b>
Сфотографуй страву з еталонним предметом (монета, ложка, тарілка)

📊 <b>Статистика та цілі</b>
Відстежуй прогрес та встановлюй денні цілі

<b>Твоя поточна ціль:</b> {daily_goal} ккал/день

Обери дію з меню нижче або просто напиши назву продукту! 👇"""
            },
            "help_message": {
                "en": """🆘 <b>Command Help</b>

<b>Basic Commands:</b>
/start - Start bot and register
/help - Show this help
/stats - Statistics for day/week/month
/goal - Set daily calorie goal
/history - Recent food entries
/clear - Clear today's data
/lang - Change language

<b>Ways to add products:</b>

1️⃣ <b>Text Search</b>
Type: "apple 150g" or "bread 50g"

2️⃣ <b>Barcode</b>
Send a photo of product barcode

3️⃣ <b>Food Photo</b>
Take a photo of your meal with reference object:
• Coin (1€, 2€)
• Cutlery (spoon, fork)
• Dishes (plate, glass)
• Credit card

<b>Query examples:</b>
• "buckwheat 100g"
• "milk 200ml"
• "banana 1 pc"
• "chicken 150g"

<b>Reference objects for photos:</b>
• 1€ coin (23.25mm)
• 2€ coin (25.75mm)
• Tablespoon (20cm)
• Plate (24cm)
• Credit card (85.6×53.98mm)

Need help? Just ask your question! 😊""",
                "ru": """🆘 <b>Справка по командам</b>

<b>Основные команды:</b>
/start - Запуск бота и регистрация
/help - Показать эту справку
/stats - Статистика за день/неделю/месяц
/goal - Установить дневную цель калорий
/history - Последние записи питания
/clear - Очистить данные за сегодня
/lang - Изменить язык

<b>Способы добавления продуктов:</b>

1️⃣ <b>Текстовый поиск</b>
Напиши: "яблоко 150г" или "хлеб 50г"

2️⃣ <b>Штрих-код</b>
Отправь фото штрих-кода товара

3️⃣ <b>Фото блюда</b>
Сфотографируй еду с эталонным предметом:
• Монета (1€, 2€)
• Столовые приборы (ложка, вилка)
• Посуда (тарелка, стакан)
• Кредитная карта

<b>Примеры запросов:</b>
• "гречка 100г"
• "молоко 200мл"
• "банан 1 шт"
• "курица 150г"

<b>Эталонные объекты для фото:</b>
• Монета 1€ (23.25мм)
• Монета 2€ (25.75мм)
• Столовая ложка (20см)
• Тарелка (24см)
• Кредитная карта (85.6×53.98мм)

Нужна помощь? Просто напиши свой вопрос! 😊""",
                "uk": """🆘 <b>Довідка по командах</b>

<b>Основні команди:</b>
/start - Запуск бота та реєстрація
/help - Показати цю довідку
/stats - Статистика за день/тиждень/місяць
/goal - Встановити денну ціль калорій
/history - Останні записи харчування
/clear - Очистити дані за сьогодні
/lang - Змінити мову

<b>Способи додавання продуктів:</b>

1️⃣ <b>Текстовий пошук</b>
Напиши: "яблуко 150г" або "хліб 50г"

2️⃣ <b>Штрих-код</b>
Надішли фото штрих-коду товару

3️⃣ <b>Фото страви</b>
Сфотографуй їжу з еталонним предметом:
• Монета (1€, 2€)
• Столові прибори (ложка, виделка)
• Посуд (тарілка, склянка)
• Кредитна картка

<b>Приклади запитів:</b>
• "гречка 100г"
• "молоко 200мл"
• "банан 1 шт"
• "курка 150г"

<b>Еталонні об'єкти для фото:</b>
• Монета 1€ (23.25мм)
• Монета 2€ (25.75мм)
• Столова ложка (20см)
• Тарілка (24см)
• Кредитна картка (85.6×53.98мм)

Потрібна допомога? Просто напиши своє питання! 😊"""
            },
            "nutrition_summary": {
                "en": "🔥 <b>{calories:.0f} kcal</b>\n🥩 Proteins: {proteins:.1f}g\n🧈 Fats: {fats:.1f}g\n🍞 Carbs: {carbs:.1f}g",
                "ru": "🔥 <b>{calories:.0f} ккал</b>\n🥩 Белки: {proteins:.1f}г\n🧈 Жиры: {fats:.1f}г\n🍞 Углеводы: {carbs:.1f}г",
                "uk": "🔥 <b>{calories:.0f} ккал</b>\n🥩 Білки: {proteins:.1f}г\n🧈 Жири: {fats:.1f}г\n🍞 Вуглеводи: {carbs:.1f}г"
            },
            "stats_message": {
                "en": """📊 <b>Nutrition Statistics</b>

👤 <b>User:</b> {name}
🎯 <b>Daily Goal:</b> {goal_calories} kcal

📅 <b>Today:</b>
{progress_bar} {progress_percent:.1f}%
🔥 Consumed: <b>{today_calories:.0f} kcal</b>
📝 Entries: {today_entries}
⚖️ Remaining: {remaining_calories:.0f} kcal

📊 <b>This Week:</b>
🔥 Total: {week_calories:.0f} kcal
📈 Average per day: {avg_daily_calories:.0f} kcal
📝 Total entries: {week_entries}

{nutrition_summary}""",
                "ru": """📊 <b>Статистика питания</b>

👤 <b>Пользователь:</b> {name}
🎯 <b>Дневная цель:</b> {goal_calories} ккал

📅 <b>Сегодня:</b>
{progress_bar} {progress_percent:.1f}%
🔥 Потреблено: <b>{today_calories:.0f} ккал</b>
📝 Записей: {today_entries}
⚖️ Осталось: {remaining_calories:.0f} ккал

📊 <b>За неделю:</b>
🔥 Всего: {week_calories:.0f} ккал
📈 В среднем в день: {avg_daily_calories:.0f} ккал
📝 Всего записей: {week_entries}

{nutrition_summary}""",
                "uk": """📊 <b>Статистика харчування</b>

👤 <b>Користувач:</b> {name}
🎯 <b>Денна ціль:</b> {goal_calories} ккал

📅 <b>Сьогодні:</b>
{progress_bar} {progress_percent:.1f}%
🔥 Спожито: <b>{today_calories:.0f} ккал</b>
📝 Записів: {today_entries}
⚖️ Залишилось: {remaining_calories:.0f} ккал

📊 <b>За тиждень:</b>
🔥 Всього: {week_calories:.0f} ккал
📈 В середньому на день: {avg_daily_calories:.0f} ккал
📝 Всього записів: {week_entries}

{nutrition_summary}"""
            },
            "main_menu": {
                "en": "🏠 <b>Main Menu</b>\n\nChoose an action:",
                "ru": "🏠 <b>Главное меню</b>\n\nВыберите действие:",
                "uk": "🏠 <b>Головне меню</b>\n\nОберіть дію:"
            },
            "settings_info": {
                "en": """⚙️ <b>Settings</b>

👤 <b>User:</b> {name}
🎯 <b>Daily Goal:</b> {daily_goal} kcal
🌍 <b>Language:</b> {language}
📅 <b>Registration:</b> {registration_date}""",
                "ru": """⚙️ <b>Настройки</b>

👤 <b>Пользователь:</b> {name}
🎯 <b>Дневная цель:</b> {daily_goal} ккал
🌍 <b>Язык:</b> {language}
📅 <b>Регистрация:</b> {registration_date}""",
                "uk": """⚙️ <b>Налаштування</b>

👤 <b>Користувач:</b> {name}
🎯 <b>Денна ціль:</b> {daily_goal} ккал
🌍 <b>Мова:</b> {language}
📅 <b>Реєстрація:</b> {registration_date}"""
            },
            "language_selection": {
                "en": "🌐 <b>Select Language</b>\n\nChoose your preferred language:",
                "ru": "🌐 <b>Выбор языка</b>\n\nВыберите предпочитаемый язык:",
                "uk": "🌐 <b>Вибір мови</b>\n\nОберіть бажану мову:"
            },
            "goal_help": {
                "en": "📊 <b>Setting Daily Goal</b>\n\nUse: <code>/goal 2000</code>\nWhere 2000 is desired calories per day\n\nRecommended values:\n• Women: 1800-2200 kcal\n• Men: 2200-2800 kcal",
                "ru": "📊 <b>Установка дневной цели</b>\n\nИспользуйте: <code>/goal 2000</code>\nГде 2000 - желаемое количество калорий в день\n\nРекомендуемые значения:\n• Женщины: 1800-2200 ккал\n• Мужчины: 2200-2800 ккал",
                "uk": "📊 <b>Встановлення денної цілі</b>\n\nВикористовуйте: <code>/goal 2000</code>\nДе 2000 - бажана кількість калорій на день\n\nРекомендовані значення:\n• Жінки: 1800-2200 ккал\n• Чоловіки: 2200-2800 ккал"
            },
            "history_header": {
                "en": "📝 <b>Recent entries:</b>",
                "ru": "📝 <b>Последние записи:</b>",
                "uk": "📝 <b>Останні записи:</b>"
            },
            "history_entry": {
                "en": "🕐 <b>{date}</b>\n🍽️ {product}\n⚖️ {quantity}g\n🔥 {calories:.0f} kcal | 🥩 {proteins:.1f}p | 🧈 {fats:.1f}f | 🍞 {carbs:.1f}c",
                "ru": "🕐 <b>{date}</b>\n🍽️ {product}\n⚖️ {quantity}г\n🔥 {calories:.0f} ккал | 🥩 {proteins:.1f}б | 🧈 {fats:.1f}ж | 🍞 {carbs:.1f}у",
                "uk": "🕐 <b>{date}</b>\n🍽️ {product}\n⚖️ {quantity}г\n🔥 {calories:.0f} ккал | 🥩 {proteins:.1f}б | 🧈 {fats:.1f}ж | 🍞 {carbs:.1f}в"
            },
            "clear_no_data": {
                "en": "📝 No entries to delete for today",
                "ru": "📝 За сегодня нет записей для удаления",
                "uk": "📝 За сьогодні немає записів для видалення"
            },
            "clear_success": {
                "en": "🗑️ <b>Data cleared</b>\n\nDeleted entries: {count}\nDate: {date}",
                "ru": "🗑️ <b>Данные очищены</b>\n\nУдалено записей: {count}\nДата: {date}",
                "uk": "🗑️ <b>Дані очищено</b>\n\nВидалено записів: {count}\nДата: {date}"
            },
            # Error messages
            "error_start": {
                "en": "❌ Error starting bot. Please try again.",
                "ru": "❌ Произошла ошибка при запуске. Попробуйте еще раз.",
                "uk": "❌ Сталася помилка при запуску. Спробуйте ще раз."
            },
            "error_stats": {
                "en": "❌ Error getting statistics",
                "ru": "❌ Ошибка при получении статистики",
                "uk": "❌ Помилка при отриманні статистики"
            },
            "error_invalid_goal": {
                "en": "❌ Invalid goal. Specify value between 800 and 5000 kcal",
                "ru": "❌ Некорректная цель. Укажите значение от 800 до 5000 ккал",
                "uk": "❌ Некоректна ціль. Вкажіть значення від 800 до 5000 ккал"
            },
            "error_invalid_number": {
                "en": "❌ Please specify a valid number of calories",
                "ru": "❌ Укажите корректное число калорий",
                "uk": "❌ Вкажіть коректне число калорій"
            },
            "error_goal_update": {
                "en": "❌ Error updating goal",
                "ru": "❌ Ошибка при обновлении цели",
                "uk": "❌ Помилка при оновленні цілі"
            },
            "error_goal_set": {
                "en": "❌ Error setting goal",
                "ru": "❌ Ошибка при установке цели",
                "uk": "❌ Помилка при встановленні цілі"
            },
            "error_history": {
                "en": "❌ Error getting history",
                "ru": "❌ Ошибка при получении истории",
                "uk": "❌ Помилка при отриманні історії"
            },
            "error_clear": {
                "en": "❌ Error clearing data",
                "ru": "❌ Ошибка при очистке данных",
                "uk": "❌ Помилка при очищенні даних"
            },
            "error_settings": {
                "en": "❌ Error loading settings",
                "ru": "❌ Ошибка при загрузке настроек",
                "uk": "❌ Помилка при завантаженні налаштувань"
            },
            "error_language_change": {
                "en": "❌ Error changing language",
                "ru": "❌ Ошибка при изменении языка",
                "uk": "❌ Помилка при зміні мови"
            }
        }
    
    def get(self, key: str, language: Language = None, **kwargs) -> str:
        """Get translated text"""
        if language is None:
            language = self.default_language
        
        if key not in self.translations:
            logger.warning(f"Translation key '{key}' not found")
            return key
        
        lang_code = language.value
        if lang_code not in self.translations[key]:
            # Fallback to English
            lang_code = Language.EN.value
            if lang_code not in self.translations[key]:
                logger.warning(f"Translation for key '{key}' not found in any language")
                return key
        
        text = self.translations[key][lang_code]
        
        # Format with provided arguments
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing format argument {e} for key '{key}'")
        
        return text
    
    def get_user_language(self, language_code: Optional[str]) -> Language:
        """Get user language from Telegram language code"""
        if not language_code:
            return self.default_language
        
        # Map Telegram language codes to our supported languages
        lang_map = {
            'en': Language.EN,
            'ru': Language.RU,
            'uk': Language.UK,
            'ua': Language.UK,  # Alternative Ukrainian code
        }
        
        # Try exact match first
        if language_code in lang_map:
            return lang_map[language_code]
        
        # Try language part only (e.g., 'en-US' -> 'en')
        lang_part = language_code.split('-')[0].lower()
        if lang_part in lang_map:
            return lang_map[lang_part]
        
        return self.default_language


# Global i18n instance
i18n = I18n()


def get_text(key: str, language: Language = None, **kwargs) -> str:
    """Convenience function to get translated text"""
    return i18n.get(key, language, **kwargs)


def get_user_language(language_code: Optional[str]) -> Language:
    """Convenience function to get user language"""
    return i18n.get_user_language(language_code)
