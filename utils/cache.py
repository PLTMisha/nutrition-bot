"""
Caching utilities for the Nutrition Bot
"""
import asyncio
import time
import logging
from typing import Any, Dict, Optional, Callable
from functools import wraps
import json
import hashlib

from config.settings import CACHE_CONFIG

logger = logging.getLogger(__name__)


class CacheManager:
    """In-memory cache manager with TTL support"""
    
    def __init__(self, max_size: int = None, default_ttl: int = None):
        self.max_size = max_size or CACHE_CONFIG["max_size"]
        self.default_ttl = default_ttl or CACHE_CONFIG["ttl"]
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = asyncio.Lock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key not in self._cache:
                return None
            
            cache_entry = self._cache[key]
            current_time = time.time()
            
            # Check if expired
            if current_time > cache_entry['expires_at']:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                return None
            
            # Update access time
            self._access_times[key] = current_time
            
            logger.debug(f"Cache hit for key: {key}")
            return cache_entry['value']
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        async with self._lock:
            current_time = time.time()
            expires_at = current_time + (ttl or self.default_ttl)
            
            # Check if we need to evict items
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict_lru()
            
            self._cache[key] = {
                'value': value,
                'created_at': current_time,
                'expires_at': expires_at
            }
            self._access_times[key] = current_time
            
            logger.debug(f"Cache set for key: {key}, TTL: {ttl or self.default_ttl}s")
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                logger.debug(f"Cache deleted for key: {key}")
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
            self._access_times.clear()
            logger.info("Cache cleared")
    
    async def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if not self._access_times:
            return
        
        # Find the least recently used key
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        
        del self._cache[lru_key]
        del self._access_times[lru_key]
        
        logger.debug(f"Evicted LRU cache entry: {lru_key}")
    
    async def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        async with self._lock:
            current_time = time.time()
            expired_keys = []
            
            for key, cache_entry in self._cache.items():
                if current_time > cache_entry['expires_at']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self._lock:
            current_time = time.time()
            expired_count = 0
            
            for cache_entry in self._cache.values():
                if current_time > cache_entry['expires_at']:
                    expired_count += 1
            
            return {
                'total_entries': len(self._cache),
                'expired_entries': expired_count,
                'active_entries': len(self._cache) - expired_count,
                'max_size': self.max_size,
                'usage_percentage': (len(self._cache) / self.max_size) * 100
            }
    
    async def close(self) -> None:
        """Close cache manager"""
        await self.clear()


def cache_result(ttl: int = None, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}_{CacheManager()._generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            try:
                result = await func(*args, **kwargs)
                await cache_manager.set(cache_key, result, ttl)
                return result
            except Exception as e:
                logger.error(f"Error in cached function {func.__name__}: {e}")
                raise
        
        return wrapper
    return decorator


class ProductCache:
    """Specialized cache for product data"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.prefix = "product:"
    
    async def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get cached product by barcode"""
        key = f"{self.prefix}barcode:{barcode}"
        return await self.cache_manager.get(key)
    
    async def set_product_by_barcode(self, barcode: str, product_data: Dict[str, Any], ttl: int = 3600) -> None:
        """Cache product by barcode"""
        key = f"{self.prefix}barcode:{barcode}"
        await self.cache_manager.set(key, product_data, ttl)
    
    async def get_search_results(self, query: str) -> Optional[list]:
        """Get cached search results"""
        key = f"{self.prefix}search:{query.lower()}"
        return await self.cache_manager.get(key)
    
    async def set_search_results(self, query: str, results: list, ttl: int = 1800) -> None:
        """Cache search results"""
        key = f"{self.prefix}search:{query.lower()}"
        await self.cache_manager.set(key, results, ttl)


class UserSessionCache:
    """Specialized cache for user sessions"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.prefix = "session:"
    
    async def get_user_session(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get cached user session"""
        key = f"{self.prefix}{telegram_id}"
        return await self.cache_manager.get(key)
    
    async def set_user_session(self, telegram_id: int, session_data: Dict[str, Any], ttl: int = 3600) -> None:
        """Cache user session"""
        key = f"{self.prefix}{telegram_id}"
        await self.cache_manager.set(key, session_data, ttl)
    
    async def delete_user_session(self, telegram_id: int) -> bool:
        """Delete user session from cache"""
        key = f"{self.prefix}{telegram_id}"
        return await self.cache_manager.delete(key)


class AnalysisCache:
    """Specialized cache for image analysis results"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.prefix = "analysis:"
    
    def _generate_image_hash(self, image_data: bytes) -> str:
        """Generate hash for image data"""
        return hashlib.sha256(image_data).hexdigest()[:16]
    
    async def get_photo_analysis(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """Get cached photo analysis"""
        image_hash = self._generate_image_hash(image_data)
        key = f"{self.prefix}photo:{image_hash}"
        return await self.cache_manager.get(key)
    
    async def set_photo_analysis(self, image_data: bytes, analysis_result: Dict[str, Any], ttl: int = 86400) -> None:
        """Cache photo analysis result"""
        image_hash = self._generate_image_hash(image_data)
        key = f"{self.prefix}photo:{image_hash}"
        await self.cache_manager.set(key, analysis_result, ttl)
    
    async def get_barcode_analysis(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """Get cached barcode analysis"""
        image_hash = self._generate_image_hash(image_data)
        key = f"{self.prefix}barcode:{image_hash}"
        return await self.cache_manager.get(key)
    
    async def set_barcode_analysis(self, image_data: bytes, analysis_result: Dict[str, Any], ttl: int = 86400) -> None:
        """Cache barcode analysis result"""
        image_hash = self._generate_image_hash(image_data)
        key = f"{self.prefix}barcode:{image_hash}"
        await self.cache_manager.set(key, analysis_result, ttl)


# Global cache manager instance
cache_manager = CacheManager()

# Specialized cache instances
product_cache = ProductCache(cache_manager)
session_cache = UserSessionCache(cache_manager)
analysis_cache = AnalysisCache(cache_manager)


async def init_cache() -> None:
    """Initialize cache system"""
    logger.info("Cache system initialized")


async def cleanup_cache() -> None:
    """Cleanup cache system"""
    await cache_manager.cleanup_expired()


async def get_cache_stats() -> Dict[str, Any]:
    """Get comprehensive cache statistics"""
    return await cache_manager.get_stats()
