"""
Handlers package initialization
"""
from aiogram import Dispatcher

from .basic import register_basic_handlers
from .food_search import register_food_search_handlers
from .media import register_media_handlers
from .nutrition import register_nutrition_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    """Register all bot handlers"""
    register_basic_handlers(dp)
    register_food_search_handlers(dp)
    register_media_handlers(dp)
    register_nutrition_handlers(dp)
