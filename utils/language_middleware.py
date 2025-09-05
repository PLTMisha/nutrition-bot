"""
Language middleware for the Nutrition Bot
"""
import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from services.database_service import DatabaseService
from utils.i18n import Language, get_user_language

logger = logging.getLogger(__name__)


class LanguageMiddleware(BaseMiddleware):
    """Middleware to inject user language into handlers"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Only process messages and callback queries
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)
        
        user_id = event.from_user.id
        telegram_lang_code = event.from_user.language_code
        
        try:
            # Get user from database
            user = await self.db_service.get_user_by_telegram_id(user_id)
            
            if user:
                # Use saved language preference
                user_lang = Language(user.language_code)
            else:
                # Use Telegram language code as fallback
                user_lang = get_user_language(telegram_lang_code)
            
            # Inject language into handler data
            data["user_language"] = user_lang
            
        except Exception as e:
            logger.error(f"Error determining user language: {e}")
            # Fallback to English
            data["user_language"] = Language.EN
        
        # Call the handler
        return await handler(event, data)
