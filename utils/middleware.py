"""
Middleware for the Nutrition Bot
"""
import logging
import time
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, Message, CallbackQuery

from services.database_service import DatabaseService
from utils.cache import CacheManager
from utils.rate_limiter import AdvancedRateLimiter
from utils.language_middleware import LanguageMiddleware

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    """Middleware to inject database service into handlers"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Inject database service into handler data
        data["db_service"] = self.db_service
        
        # Call the handler
        return await handler(event, data)


class CacheMiddleware(BaseMiddleware):
    """Middleware to inject cache manager into handlers"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Inject cache manager into handler data
        data["cache_manager"] = self.cache_manager
        
        # Call the handler
        return await handler(event, data)


class RateLimitMiddleware(BaseMiddleware):
    """Middleware for rate limiting"""
    
    def __init__(self, rate_limiter: AdvancedRateLimiter):
        self.rate_limiter = rate_limiter
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Only apply rate limiting to messages and callback queries
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)
        
        user_id = event.from_user.id
        
        # Determine operation type based on event
        operation = self._determine_operation(event)
        
        # Check rate limit
        is_allowed, retry_after = self.rate_limiter.is_allowed(user_id, operation)
        
        if not is_allowed:
            # Send rate limit message
            if isinstance(event, Message):
                await event.answer(
                    f"⏰ <b>Превышен лимит запросов</b>\n\n"
                    f"Попробуйте снова через {retry_after} секунд.\n"
                    f"Это ограничение помогает поддерживать стабильную работу бота для всех пользователей."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    f"Превышен лимит запросов. Попробуйте через {retry_after} сек.",
                    show_alert=True
                )
            return
        
        # Inject rate limiter into handler data
        data["rate_limiter"] = self.rate_limiter
        
        # Call the handler
        return await handler(event, data)
    
    def _determine_operation(self, event: TelegramObject) -> str:
        """Determine operation type from event"""
        if isinstance(event, Message):
            if event.photo:
                return 'image_analysis'
            elif event.text and any(keyword in event.text.lower() for keyword in ['поиск', 'найти', 'search']):
                return 'search'
            else:
                return 'general'
        elif isinstance(event, CallbackQuery):
            if event.data and 'barcode' in event.data:
                return 'barcode'
            elif event.data and 'search' in event.data:
                return 'search'
            else:
                return 'general'
        
        return 'general'


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging user interactions"""
    
    def __init__(self):
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()
        
        # Log incoming event
        if isinstance(event, Message):
            user_info = f"@{event.from_user.username}" if event.from_user.username else f"ID:{event.from_user.id}"
            content_type = "text" if event.text else "photo" if event.photo else "other"
            logger.info(f"Message from {user_info}: {content_type}")
            
        elif isinstance(event, CallbackQuery):
            user_info = f"@{event.from_user.username}" if event.from_user.username else f"ID:{event.from_user.id}"
            logger.info(f"Callback from {user_info}: {event.data}")
        
        try:
            # Call the handler
            result = await handler(event, data)
            
            # Log successful completion
            processing_time = time.time() - start_time
            logger.info(f"Handler completed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            # Log error
            processing_time = time.time() - start_time
            logger.error(f"Handler failed after {processing_time:.2f}s: {e}")
            
            # Send error message to user
            if isinstance(event, Message):
                await event.answer(
                    "❌ Произошла ошибка при обработке запроса. Попробуйте еще раз."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer("Произошла ошибка. Попробуйте еще раз.", show_alert=True)
            
            raise


class UserActivityMiddleware(BaseMiddleware):
    """Middleware to track user activity with fallback protection"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Update user activity for messages and callback queries
        if isinstance(event, (Message, CallbackQuery)):
            try:
                # Update user's last activity with timeout protection
                import asyncio
                await asyncio.wait_for(
                    self.db_service.create_or_get_user(
                        telegram_id=event.from_user.id,
                        username=event.from_user.username,
                        first_name=event.from_user.first_name,
                        last_name=event.from_user.last_name,
                        language_code=event.from_user.language_code or "en"
                    ),
                    timeout=3.0  # 3 second timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"User activity update timeout for user {event.from_user.id} (non-critical)")
            except Exception as e:
                logger.warning(f"Failed to update user activity for user {event.from_user.id}: {e} (non-critical)")
        
        # Call the handler (ALWAYS continue regardless of DB issues)
        return await handler(event, data)


class SecurityMiddleware(BaseMiddleware):
    """Middleware for security checks"""
    
    def __init__(self):
        self.blocked_users = set()  # In production, use database
        self.suspicious_patterns = [
            'script',
            'javascript',
            'eval(',
            'exec(',
            '<script',
            'onload=',
            'onerror=',
        ]
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Security checks for messages
        if isinstance(event, Message):
            user_id = event.from_user.id
            
            # Check if user is blocked
            if user_id in self.blocked_users:
                logger.warning(f"Blocked user {user_id} attempted to use bot")
                return
            
            # Check for suspicious content
            if event.text:
                text_lower = event.text.lower()
                for pattern in self.suspicious_patterns:
                    if pattern in text_lower:
                        logger.warning(f"Suspicious content from user {user_id}: {pattern}")
                        await event.answer("❌ Обнаружен подозрительный контент.")
                        return
            
            # Check message length
            if event.text and len(event.text) > 1000:
                logger.warning(f"Oversized message from user {user_id}: {len(event.text)} chars")
                await event.answer("❌ Сообщение слишком длинное.")
                return
        
        # Call the handler
        return await handler(event, data)


class MetricsMiddleware(BaseMiddleware):
    """Middleware for collecting metrics"""
    
    def __init__(self):
        self.metrics = {
            'total_messages': 0,
            'total_callbacks': 0,
            'total_photos': 0,
            'total_errors': 0,
            'response_times': [],
        }
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()
        
        # Count events
        if isinstance(event, Message):
            self.metrics['total_messages'] += 1
            if event.photo:
                self.metrics['total_photos'] += 1
        elif isinstance(event, CallbackQuery):
            self.metrics['total_callbacks'] += 1
        
        try:
            # Call the handler
            result = await handler(event, data)
            
            # Record response time
            response_time = time.time() - start_time
            self.metrics['response_times'].append(response_time)
            
            # Keep only last 1000 response times
            if len(self.metrics['response_times']) > 1000:
                self.metrics['response_times'] = self.metrics['response_times'][-1000:]
            
            return result
            
        except Exception as e:
            self.metrics['total_errors'] += 1
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        response_times = self.metrics['response_times']
        
        return {
            'total_messages': self.metrics['total_messages'],
            'total_callbacks': self.metrics['total_callbacks'],
            'total_photos': self.metrics['total_photos'],
            'total_errors': self.metrics['total_errors'],
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
        }


def setup_middlewares(
    dp,
    db_service: DatabaseService,
    cache_manager: CacheManager,
    rate_limiter: AdvancedRateLimiter
) -> None:
    """Setup all middlewares for the dispatcher"""
    
    # Security middleware (first)
    dp.message.middleware(SecurityMiddleware())
    dp.callback_query.middleware(SecurityMiddleware())
    
    # Rate limiting middleware
    dp.message.middleware(RateLimitMiddleware(rate_limiter))
    dp.callback_query.middleware(RateLimitMiddleware(rate_limiter))
    
    # User activity tracking
    dp.message.middleware(UserActivityMiddleware(db_service))
    dp.callback_query.middleware(UserActivityMiddleware(db_service))
    
    # Logging middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    # Metrics collection
    metrics_middleware = MetricsMiddleware()
    dp.message.middleware(metrics_middleware)
    dp.callback_query.middleware(metrics_middleware)
    
    # Language middleware (before service injection)
    dp.message.middleware(LanguageMiddleware(db_service))
    dp.callback_query.middleware(LanguageMiddleware(db_service))
    
    # Service injection middlewares
    dp.message.middleware(DatabaseMiddleware(db_service))
    dp.callback_query.middleware(DatabaseMiddleware(db_service))
    
    dp.message.middleware(CacheMiddleware(cache_manager))
    dp.callback_query.middleware(CacheMiddleware(cache_manager))
    
    # Store metrics middleware for access
    dp["metrics_middleware"] = metrics_middleware
    
    logger.info("All middlewares setup completed")
