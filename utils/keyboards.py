"""
Keyboard utilities for the Nutrition Bot with i18n support
"""
from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from utils.i18n import Language, get_text


def get_main_menu_keyboard(lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get main menu inline keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text("btn_search", lang), callback_data="search_products"),
            InlineKeyboardButton(text=get_text("btn_scan_barcode", lang), callback_data="scan_barcode")
        ],
        [
            InlineKeyboardButton(text=get_text("btn_photo_analysis", lang), callback_data="analyze_photo"),
            InlineKeyboardButton(text=get_text("btn_statistics", lang), callback_data="view_stats")
        ],
        [
            InlineKeyboardButton(text=get_text("btn_history", lang), callback_data="show_history"),
            InlineKeyboardButton(text=get_text("btn_settings", lang), callback_data="settings")
        ],
        [
            InlineKeyboardButton(text=get_text("btn_language", lang), callback_data="change_language")
        ]
    ])
    return keyboard


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
        ],
        [
            InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk")
        ],
        [
            InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
        ]
    ])
    return keyboard


def get_settings_keyboard(lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get settings inline keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎯 " + get_text("goal_usage", lang).split('\n')[0].replace("📊 <b>", "").replace("</b>", ""), callback_data="change_goal"),
            InlineKeyboardButton(text=get_text("btn_language", lang), callback_data="change_language")
        ],
        [
            InlineKeyboardButton(text="🔔 Notifications", callback_data="toggle_notifications"),
            InlineKeyboardButton(text="📊 My Data", callback_data="my_data")
        ],
        [
            InlineKeyboardButton(text="🗑️ Clear Data", callback_data="clear_data"),
            InlineKeyboardButton(text=get_text("btn_export", lang), callback_data="export_data")
        ],
        [
            InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")
        ]
    ])
    return keyboard


def get_stats_keyboard(lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get statistics keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text("btn_weekly_chart", lang), callback_data="weekly_chart"),
            InlineKeyboardButton(text=get_text("btn_monthly_chart", lang), callback_data="monthly_chart")
        ],
        [
            InlineKeyboardButton(text=get_text("btn_export", lang), callback_data="export_data"),
            InlineKeyboardButton(text="🗑️ Delete Last", callback_data="delete_last")
        ],
        [
            InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")
        ]
    ])
    return keyboard


def get_search_keyboard(lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get search options keyboard"""
    # Category names by language
    categories = {
        Language.EN: {
            "bread": "🥖 Bread & Bakery",
            "dairy": "🥛 Dairy Products",
            "meat": "🍖 Meat & Fish",
            "vegetables": "🥬 Fruits & Vegetables",
            "grains": "🍝 Grains & Pasta",
            "sweets": "🍫 Sweets",
            "drinks": "🥤 Drinks",
            "snacks": "🍿 Snacks",
            "search_by_name": "🔍 Search by Name"
        },
        Language.RU: {
            "bread": "🥖 Хлеб и выпечка",
            "dairy": "🥛 Молочные продукты",
            "meat": "🍖 Мясо и рыба",
            "vegetables": "🥬 Овощи и фрукты",
            "grains": "🍝 Крупы и макароны",
            "sweets": "🍫 Сладости",
            "drinks": "🥤 Напитки",
            "snacks": "🍿 Снеки",
            "search_by_name": "🔍 Поиск по названию"
        },
        Language.UK: {
            "bread": "🥖 Хліб та випічка",
            "dairy": "🥛 Молочні продукти",
            "meat": "🍖 М'ясо та риба",
            "vegetables": "🥬 Овочі та фрукти",
            "grains": "🍝 Крупи та макарони",
            "sweets": "🍫 Солодощі",
            "drinks": "🥤 Напої",
            "snacks": "🍿 Снеки",
            "search_by_name": "🔍 Пошук за назвою"
        }
    }
    
    cat = categories.get(lang, categories[Language.EN])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=cat["bread"], callback_data="search_category_bread"),
            InlineKeyboardButton(text=cat["dairy"], callback_data="search_category_dairy")
        ],
        [
            InlineKeyboardButton(text=cat["meat"], callback_data="search_category_meat"),
            InlineKeyboardButton(text=cat["vegetables"], callback_data="search_category_vegetables")
        ],
        [
            InlineKeyboardButton(text=cat["grains"], callback_data="search_category_grains"),
            InlineKeyboardButton(text=cat["sweets"], callback_data="search_category_sweets")
        ],
        [
            InlineKeyboardButton(text=cat["drinks"], callback_data="search_category_drinks"),
            InlineKeyboardButton(text=cat["snacks"], callback_data="search_category_snacks")
        ],
        [
            InlineKeyboardButton(text=cat["search_by_name"], callback_data="search_by_name")
        ],
        [
            InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")
        ]
    ])
    return keyboard


def get_product_selection_keyboard(products: List[dict], page: int = 0, per_page: int = 5, lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get product selection keyboard with pagination"""
    keyboard_buttons = []
    
    # Calculate pagination
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_products = products[start_idx:end_idx]
    
    # Add product buttons
    for i, product in enumerate(page_products):
        product_idx = start_idx + i
        product_name = product.get('name', 'Unknown Product')
        brand = product.get('brand', '')
        
        # Truncate long names
        display_name = product_name[:30] + "..." if len(product_name) > 30 else product_name
        if brand:
            display_name = f"{brand} - {display_name}"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=display_name,
                callback_data=f"select_product_{product_idx}"
            )
        ])
    
    # Add pagination buttons
    pagination_buttons = []
    if page > 0:
        back_text = {"en": "⬅️ Back", "ru": "⬅️ Назад", "uk": "⬅️ Назад"}
        pagination_buttons.append(
            InlineKeyboardButton(text=back_text.get(lang.value, back_text["en"]), callback_data=f"products_page_{page-1}")
        )
    
    if end_idx < len(products):
        next_text = {"en": "➡️ Next", "ru": "➡️ Далее", "uk": "➡️ Далі"}
        pagination_buttons.append(
            InlineKeyboardButton(text=next_text.get(lang.value, next_text["en"]), callback_data=f"products_page_{page+1}")
        )
    
    if pagination_buttons:
        keyboard_buttons.append(pagination_buttons)
    
    # Add back to search button
    new_search_text = {"en": "🔍 New Search", "ru": "🔍 Новый поиск", "uk": "🔍 Новий пошук"}
    keyboard_buttons.append([
        InlineKeyboardButton(text=new_search_text.get(lang.value, new_search_text["en"]), callback_data="search_products"),
        InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_quantity_keyboard(product_id: str, lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get quantity selection keyboard"""
    manual_text = {"en": "✏️ Enter manually", "ru": "✏️ Ввести вручную", "uk": "✏️ Ввести вручну"}
    other_product_text = {"en": "🔍 Other product", "ru": "🔍 Другой продукт", "uk": "🔍 Інший продукт"}
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="50г", callback_data=f"quantity_{product_id}_50"),
            InlineKeyboardButton(text="100г", callback_data=f"quantity_{product_id}_100"),
            InlineKeyboardButton(text="150г", callback_data=f"quantity_{product_id}_150")
        ],
        [
            InlineKeyboardButton(text="200г", callback_data=f"quantity_{product_id}_200"),
            InlineKeyboardButton(text="250г", callback_data=f"quantity_{product_id}_250"),
            InlineKeyboardButton(text="300г", callback_data=f"quantity_{product_id}_300")
        ],
        [
            InlineKeyboardButton(text=manual_text.get(lang.value, manual_text["en"]), callback_data=f"quantity_custom_{product_id}")
        ],
        [
            InlineKeyboardButton(text=other_product_text.get(lang.value, other_product_text["en"]), callback_data="search_products"),
            InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")
        ]
    ])
    return keyboard


def get_meal_type_keyboard(product_id: str, quantity: str, lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get meal type selection keyboard"""
    meals = {
        Language.EN: {
            "breakfast": "🌅 Breakfast",
            "lunch": "🌞 Lunch", 
            "dinner": "🌆 Dinner",
            "snack": "🍿 Snack",
            "skip": "➡️ Skip"
        },
        Language.RU: {
            "breakfast": "🌅 Завтрак",
            "lunch": "🌞 Обед",
            "dinner": "🌆 Ужин", 
            "snack": "🍿 Перекус",
            "skip": "➡️ Пропустить"
        },
        Language.UK: {
            "breakfast": "🌅 Сніданок",
            "lunch": "🌞 Обід",
            "dinner": "🌆 Вечеря",
            "snack": "🍿 Перекус",
            "skip": "➡️ Пропустити"
        }
    }
    
    meal = meals.get(lang, meals[Language.EN])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=meal["breakfast"], callback_data=f"meal_{product_id}_{quantity}_breakfast"),
            InlineKeyboardButton(text=meal["lunch"], callback_data=f"meal_{product_id}_{quantity}_lunch")
        ],
        [
            InlineKeyboardButton(text=meal["dinner"], callback_data=f"meal_{product_id}_{quantity}_dinner"),
            InlineKeyboardButton(text=meal["snack"], callback_data=f"meal_{product_id}_{quantity}_snack")
        ],
        [
            InlineKeyboardButton(text=meal["skip"], callback_data=f"meal_{product_id}_{quantity}_skip")
        ]
    ])
    return keyboard


def get_confirmation_keyboard(action: str, data: str = "", lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get confirmation keyboard"""
    yes_text = {"en": "✅ Yes", "ru": "✅ Да", "uk": "✅ Так"}
    no_text = {"en": "❌ No", "ru": "❌ Нет", "uk": "❌ Ні"}
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=yes_text.get(lang.value, yes_text["en"]), callback_data=f"confirm_{action}_{data}"),
            InlineKeyboardButton(text=no_text.get(lang.value, no_text["en"]), callback_data=f"cancel_{action}")
        ]
    ])
    return keyboard


def get_stats_period_keyboard(lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get statistics period selection keyboard"""
    periods = {
        Language.EN: {
            "today": "📅 Today",
            "week": "📊 Week",
            "month": "📈 Month",
            "all": "📋 All time"
        },
        Language.RU: {
            "today": "📅 Сегодня",
            "week": "📊 Неделя",
            "month": "📈 Месяц",
            "all": "📋 Все время"
        },
        Language.UK: {
            "today": "📅 Сьогодні",
            "week": "📊 Тиждень",
            "month": "📈 Місяць",
            "all": "📋 Весь час"
        }
    }
    
    period = periods.get(lang, periods[Language.EN])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=period["today"], callback_data="stats_today"),
            InlineKeyboardButton(text=period["week"], callback_data="stats_week")
        ],
        [
            InlineKeyboardButton(text=period["month"], callback_data="stats_month"),
            InlineKeyboardButton(text=period["all"], callback_data="stats_all")
        ],
        [
            InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")
        ]
    ])
    return keyboard


def get_history_keyboard(page: int = 0, has_next: bool = False, lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get history navigation keyboard"""
    keyboard_buttons = []
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        back_text = {"en": "⬅️ Back", "ru": "⬅️ Назад", "uk": "⬅️ Назад"}
        nav_buttons.append(
            InlineKeyboardButton(text=back_text.get(lang.value, back_text["en"]), callback_data=f"history_page_{page-1}")
        )
    if has_next:
        next_text = {"en": "➡️ Next", "ru": "➡️ Далее", "uk": "➡️ Далі"}
        nav_buttons.append(
            InlineKeyboardButton(text=next_text.get(lang.value, next_text["en"]), callback_data=f"history_page_{page+1}")
        )
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    # Action buttons
    delete_text = {"en": "🗑️ Delete Entry", "ru": "🗑️ Удалить запись", "uk": "🗑️ Видалити запис"}
    keyboard_buttons.extend([
        [
            InlineKeyboardButton(text=delete_text.get(lang.value, delete_text["en"]), callback_data="delete_log_entry"),
            InlineKeyboardButton(text=get_text("btn_statistics", lang), callback_data="view_stats")
        ],
        [
            InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")
        ]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_photo_analysis_keyboard(lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get photo analysis options keyboard"""
    options = {
        Language.EN: {
            "upload": "📷 Upload Photo",
            "instructions": "ℹ️ Instructions",
            "reference": "📏 Reference Objects",
            "tips": "💡 Tips"
        },
        Language.RU: {
            "upload": "📷 Загрузить фото",
            "instructions": "ℹ️ Инструкция",
            "reference": "📏 Эталонные объекты",
            "tips": "💡 Советы"
        },
        Language.UK: {
            "upload": "📷 Завантажити фото",
            "instructions": "ℹ️ Інструкція",
            "reference": "📏 Еталонні об'єкти",
            "tips": "💡 Поради"
        }
    }
    
    opt = options.get(lang, options[Language.EN])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=opt["upload"], callback_data="upload_photo"),
            InlineKeyboardButton(text=opt["instructions"], callback_data="photo_instructions")
        ],
        [
            InlineKeyboardButton(text=opt["reference"], callback_data="reference_objects"),
            InlineKeyboardButton(text=opt["tips"], callback_data="photo_tips")
        ],
        [
            InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")
        ]
    ])
    return keyboard


def get_barcode_scan_keyboard(lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get barcode scanning options keyboard"""
    options = {
        Language.EN: {
            "scan": "📷 Scan Code",
            "instructions": "ℹ️ How to Scan",
            "manual": "🔢 Enter Code Manually"
        },
        Language.RU: {
            "scan": "📷 Сканировать код",
            "instructions": "ℹ️ Как сканировать",
            "manual": "🔢 Ввести код вручную"
        },
        Language.UK: {
            "scan": "📷 Сканувати код",
            "instructions": "ℹ️ Як сканувати",
            "manual": "🔢 Ввести код вручну"
        }
    }
    
    opt = options.get(lang, options[Language.EN])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=opt["scan"], callback_data="scan_barcode_now"),
            InlineKeyboardButton(text=opt["instructions"], callback_data="barcode_instructions")
        ],
        [
            InlineKeyboardButton(text=opt["manual"], callback_data="enter_barcode_manual")
        ],
        [
            InlineKeyboardButton(text=get_text("btn_main_menu", lang), callback_data="main_menu")
        ]
    ])
    return keyboard


def get_analysis_result_keyboard(analysis_id: str, lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get keyboard for photo analysis results"""
    options = {
        Language.EN: {
            "add": "✅ Add as is",
            "edit": "✏️ Change weight",
            "reanalyze": "🔄 Analyze again",
            "cancel": "❌ Cancel"
        },
        Language.RU: {
            "add": "✅ Добавить как есть",
            "edit": "✏️ Изменить вес",
            "reanalyze": "🔄 Анализировать заново",
            "cancel": "❌ Отменить"
        },
        Language.UK: {
            "add": "✅ Додати як є",
            "edit": "✏️ Змінити вагу",
            "reanalyze": "🔄 Аналізувати знову",
            "cancel": "❌ Скасувати"
        }
    }
    
    opt = options.get(lang, options[Language.EN])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=opt["add"], callback_data=f"add_analysis_{analysis_id}"),
            InlineKeyboardButton(text=opt["edit"], callback_data=f"edit_weight_{analysis_id}")
        ],
        [
            InlineKeyboardButton(text=opt["reanalyze"], callback_data="analyze_photo"),
            InlineKeyboardButton(text=opt["cancel"], callback_data="main_menu")
        ]
    ])
    return keyboard


def get_cancel_keyboard(lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get simple cancel keyboard"""
    cancel_text = {"en": "❌ Cancel", "ru": "❌ Отменить", "uk": "❌ Скасувати"}
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=cancel_text.get(lang.value, cancel_text["en"]), callback_data="main_menu")
        ]
    ])
    return keyboard


def get_back_keyboard(callback_data: str = "main_menu", lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get simple back keyboard"""
    back_text = {"en": "⬅️ Back", "ru": "⬅️ Назад", "uk": "⬅️ Назад"}
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=back_text.get(lang.value, back_text["en"]), callback_data=callback_data)
        ]
    ])
    return keyboard


def get_yes_no_keyboard(yes_callback: str, no_callback: str, lang: Language = Language.EN) -> InlineKeyboardMarkup:
    """Get yes/no keyboard with custom callbacks"""
    yes_text = {"en": "✅ Yes", "ru": "✅ Да", "uk": "✅ Так"}
    no_text = {"en": "❌ No", "ru": "❌ Нет", "uk": "❌ Ні"}
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=yes_text.get(lang.value, yes_text["en"]), callback_data=yes_callback),
            InlineKeyboardButton(text=no_text.get(lang.value, no_text["en"]), callback_data=no_callback)
        ]
    ])
    return keyboard


# Reply keyboards for specific interactions

def get_share_contact_keyboard(lang: Language = Language.EN) -> ReplyKeyboardMarkup:
    """Get keyboard to share contact (for premium features)"""
    share_text = {"en": "📱 Share Contact", "ru": "📱 Поделиться контактом", "uk": "📱 Поділитися контактом"}
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=share_text.get(lang.value, share_text["en"]), request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_language_selection_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard (alias for get_language_keyboard)"""
    return get_language_keyboard()


def get_remove_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard to remove reply keyboard"""
    return ReplyKeyboardMarkup(
        keyboard=[],
        resize_keyboard=True,
        remove_keyboard=True
    )
