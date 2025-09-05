"""
Rate limiting utilities for the Nutrition Bot
"""
import time
import logging
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque

from config.settings import RATE_LIMIT_CONFIG

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter with sliding window"""
    
    def __init__(self, requests_per_window: int = None, window_seconds: int = None):
        self.requests_per_window = requests_per_window or RATE_LIMIT_CONFIG["requests"]
        self.window_seconds = window_seconds or RATE_LIMIT_CONFIG["window"]
        
        # Store request timestamps for each user
        self._user_requests: Dict[int, deque] = defaultdict(deque)
        
        # Store last cleanup time
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes
    
    def is_allowed(self, user_id: int) -> Tuple[bool, Optional[int]]:
        """
        Check if request is allowed for user
        
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        current_time = time.time()
        
        # Cleanup old entries periodically
        if current_time - self._last_cleanup > self._cleanup_interval:
            self.cleanup()
        
        user_requests = self._user_requests[user_id]
        
        # Remove requests outside the current window
        cutoff_time = current_time - self.window_seconds
        while user_requests and user_requests[0] < cutoff_time:
            user_requests.popleft()
        
        # Check if user has exceeded the limit
        if len(user_requests) >= self.requests_per_window:
            # Calculate when the oldest request will expire
            oldest_request = user_requests[0]
            retry_after = int(oldest_request + self.window_seconds - current_time) + 1
            
            logger.warning(f"Rate limit exceeded for user {user_id}. Retry after {retry_after}s")
            return False, retry_after
        
        # Add current request
        user_requests.append(current_time)
        
        logger.debug(f"Request allowed for user {user_id}. Count: {len(user_requests)}/{self.requests_per_window}")
        return True, None
    
    def get_remaining_requests(self, user_id: int) -> int:
        """Get remaining requests for user in current window"""
        current_time = time.time()
        user_requests = self._user_requests[user_id]
        
        # Remove requests outside the current window
        cutoff_time = current_time - self.window_seconds
        while user_requests and user_requests[0] < cutoff_time:
            user_requests.popleft()
        
        return max(0, self.requests_per_window - len(user_requests))
    
    def get_reset_time(self, user_id: int) -> Optional[int]:
        """Get timestamp when rate limit resets for user"""
        user_requests = self._user_requests[user_id]
        
        if not user_requests:
            return None
        
        # The limit resets when the oldest request expires
        oldest_request = user_requests[0]
        return int(oldest_request + self.window_seconds)
    
    def cleanup(self) -> int:
        """Remove old request data to free memory"""
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        cleaned_users = 0
        users_to_remove = []
        
        for user_id, user_requests in self._user_requests.items():
            # Remove old requests
            while user_requests and user_requests[0] < cutoff_time:
                user_requests.popleft()
            
            # Remove users with no recent requests
            if not user_requests:
                users_to_remove.append(user_id)
        
        # Remove empty user entries
        for user_id in users_to_remove:
            del self._user_requests[user_id]
            cleaned_users += 1
        
        self._last_cleanup = current_time
        
        if cleaned_users > 0:
            logger.info(f"Rate limiter cleanup: removed {cleaned_users} inactive users")
        
        return cleaned_users
    
    def reset_user(self, user_id: int) -> None:
        """Reset rate limit for specific user"""
        if user_id in self._user_requests:
            del self._user_requests[user_id]
            logger.info(f"Rate limit reset for user {user_id}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get rate limiter statistics"""
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        active_users = 0
        total_requests = 0
        
        for user_requests in self._user_requests.values():
            # Count only recent requests
            recent_requests = sum(1 for req_time in user_requests if req_time >= cutoff_time)
            if recent_requests > 0:
                active_users += 1
                total_requests += recent_requests
        
        return {
            'active_users': active_users,
            'total_recent_requests': total_requests,
            'requests_per_window': self.requests_per_window,
            'window_seconds': self.window_seconds
        }


class AdvancedRateLimiter:
    """Advanced rate limiter with different limits for different operations"""
    
    def __init__(self):
        # Different limits for different operations
        self.limiters = {
            'general': RateLimiter(30, 60),      # 30 requests per minute
            'search': RateLimiter(20, 60),       # 20 searches per minute
            'image_analysis': RateLimiter(5, 60), # 5 image analyses per minute
            'barcode': RateLimiter(10, 60),      # 10 barcode scans per minute
        }
    
    def is_allowed(self, user_id: int, operation: str = 'general') -> Tuple[bool, Optional[int]]:
        """Check if operation is allowed for user"""
        limiter = self.limiters.get(operation, self.limiters['general'])
        return limiter.is_allowed(user_id)
    
    def get_remaining_requests(self, user_id: int, operation: str = 'general') -> int:
        """Get remaining requests for user and operation"""
        limiter = self.limiters.get(operation, self.limiters['general'])
        return limiter.get_remaining_requests(user_id)
    
    def cleanup(self) -> Dict[str, int]:
        """Cleanup all limiters"""
        cleanup_stats = {}
        for operation, limiter in self.limiters.items():
            cleanup_stats[operation] = limiter.cleanup()
        return cleanup_stats
    
    def reset_user(self, user_id: int, operation: Optional[str] = None) -> None:
        """Reset rate limit for user (all operations or specific operation)"""
        if operation:
            if operation in self.limiters:
                self.limiters[operation].reset_user(user_id)
        else:
            for limiter in self.limiters.values():
                limiter.reset_user(user_id)
    
    def get_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for all limiters"""
        stats = {}
        for operation, limiter in self.limiters.items():
            stats[operation] = limiter.get_stats()
        return stats


def rate_limit_middleware(operation: str = 'general'):
    """Middleware decorator for rate limiting"""
    def decorator(func):
        async def wrapper(message, *args, **kwargs):
            user_id = message.from_user.id
            
            # Get rate limiter from context or use global instance
            rate_limiter = getattr(message.bot, 'rate_limiter', None)
            if not rate_limiter:
                # Fallback to simple rate limiter
                rate_limiter = RateLimiter()
            
            # Check rate limit
            is_allowed, retry_after = rate_limiter.is_allowed(user_id, operation)
            
            if not is_allowed:
                # Send rate limit message
                await message.answer(
                    f"⏰ <b>Превышен лимит запросов</b>\n\n"
                    f"Попробуйте снова через {retry_after} секунд.\n"
                    f"Это ограничение помогает поддерживать стабильную работу бота для всех пользователей."
                )
                return
            
            # Execute original function
            return await func(message, *args, **kwargs)
        
        return wrapper
    return decorator


class UserQuotaManager:
    """Manage daily/monthly quotas for users"""
    
    def __init__(self):
        self.daily_quotas = {
            'image_analysis': 50,    # 50 image analyses per day
            'barcode_scans': 100,    # 100 barcode scans per day
            'searches': 200,         # 200 searches per day
        }
        
        self.monthly_quotas = {
            'image_analysis': 1000,  # 1000 image analyses per month
            'barcode_scans': 2000,   # 2000 barcode scans per month
            'searches': 5000,        # 5000 searches per month
        }
        
        # In-memory storage (in production, use Redis or database)
        self.daily_usage: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.monthly_usage: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        self.last_daily_reset = time.time()
        self.last_monthly_reset = time.time()
    
    def check_quota(self, user_id: int, operation: str) -> Tuple[bool, str]:
        """Check if user has quota remaining for operation"""
        # Check daily quota
        daily_used = self.daily_usage[user_id][operation]
        daily_limit = self.daily_quotas.get(operation, float('inf'))
        
        if daily_used >= daily_limit:
            return False, f"daily limit of {daily_limit} exceeded"
        
        # Check monthly quota
        monthly_used = self.monthly_usage[user_id][operation]
        monthly_limit = self.monthly_quotas.get(operation, float('inf'))
        
        if monthly_used >= monthly_limit:
            return False, f"monthly limit of {monthly_limit} exceeded"
        
        return True, "quota available"
    
    def use_quota(self, user_id: int, operation: str) -> None:
        """Use quota for operation"""
        self.daily_usage[user_id][operation] += 1
        self.monthly_usage[user_id][operation] += 1
    
    def get_usage(self, user_id: int) -> Dict[str, Dict[str, int]]:
        """Get usage statistics for user"""
        return {
            'daily': dict(self.daily_usage[user_id]),
            'monthly': dict(self.monthly_usage[user_id])
        }
    
    def reset_daily_quotas(self) -> None:
        """Reset daily quotas (called by scheduler)"""
        self.daily_usage.clear()
        self.last_daily_reset = time.time()
        logger.info("Daily quotas reset")
    
    def reset_monthly_quotas(self) -> None:
        """Reset monthly quotas (called by scheduler)"""
        self.monthly_usage.clear()
        self.last_monthly_reset = time.time()
        logger.info("Monthly quotas reset")


# Global instances
rate_limiter = AdvancedRateLimiter()
quota_manager = UserQuotaManager()
