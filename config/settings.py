"""
Configuration settings for the Nutrition Bot
"""
import os
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Telegram Bot
    telegram_bot_token: str
    
    # Database
    neon_database_url: str
    
    # Vercel API
    vercel_api_url: str
    vercel_api_key: Optional[str] = None
    
    # Langdock API (replaces OpenAI)
    langdock_api_key: Optional[str] = None
    
    # Open Food Facts
    openfoodfacts_api_url: str = "https://world.openfoodfacts.org/api"
    
    # Railway
    railway_environment: str = "development"
    port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    
    # Rate Limiting
    rate_limit_requests: int = 30
    rate_limit_window: int = 60
    
    # Cache
    cache_ttl: int = 3600
    max_cache_size: int = 1000
    
    # Image Processing
    max_image_size: int = 10485760  # 10MB
    allowed_image_types: List[str] = ["jpg", "jpeg", "png", "webp"]
    
    # Health Check
    health_check_interval: int = 300
    
    @validator('allowed_image_types', pre=True)
    def parse_image_types(cls, v):
        if isinstance(v, str):
            return [t.strip() for t in v.split(',')]
        return v
    
    @validator('telegram_bot_token')
    def validate_bot_token(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Invalid Telegram bot token')
        return v
    
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Database configuration
DATABASE_CONFIG = {
    "url": settings.neon_database_url,
    "echo": settings.log_level == "DEBUG",
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600,
}

# Telegram bot configuration
BOT_CONFIG = {
    "token": settings.telegram_bot_token,
    "parse_mode": "HTML",
    "disable_web_page_preview": True,
}

# Langdock configuration (replaces OpenAI)
LANGDOCK_CONFIG = {
    "api_key": settings.langdock_api_key,
    "base_url": "https://api.langdock.com/v1",
    "model": "gpt-4-vision-preview",
    "max_tokens": 1000,
    "temperature": 0.1,
}

# Cache configuration
CACHE_CONFIG = {
    "ttl": settings.cache_ttl,
    "max_size": settings.max_cache_size,
}

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "requests": settings.rate_limit_requests,
    "window": settings.rate_limit_window,
}

# Image processing configuration
IMAGE_CONFIG = {
    "max_size": settings.max_image_size,
    "allowed_types": settings.allowed_image_types,
    "quality": 85,
    "max_width": 1920,
    "max_height": 1080,
}

# Vercel API configuration
VERCEL_CONFIG = {
    "base_url": settings.vercel_api_url,
    "api_key": settings.vercel_api_key,
    "timeout": 30,
    "retries": 3,
}

# Open Food Facts configuration
OPENFOODFACTS_CONFIG = {
    "base_url": settings.openfoodfacts_api_url,
    "user_agent": "NutritionBot/1.0",
    "timeout": 10,
    "retries": 2,
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.log_level,
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "nutrition_bot.log",
            "mode": "a",
        },
    },
    "loggers": {
        "": {
            "level": settings.log_level,
            "handlers": ["console", "file"],
        },
        "aiogram": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "sqlalchemy": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
