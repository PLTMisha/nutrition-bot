"""
Configuration settings for the Nutrition Bot
"""
import os
from typing import List, Optional

# Debug: Print all environment variables for Railway debugging
print("=== ENVIRONMENT VARIABLES DEBUG ===")
for key, value in os.environ.items():
    if any(keyword in key.upper() for keyword in ['TELEGRAM', 'NEON', 'VERCEL', 'LANGDOCK', 'RAILWAY', 'PORT']):
        print(f"{key}={value[:20]}..." if len(value) > 20 else f"{key}={value}")
print("=== END DEBUG ===")

# Direct environment variable access to bypass Pydantic issues
def get_env_var(name: str, default: str = None, required: bool = True) -> str:
    """Get environment variable with fallback to lowercase version"""
    value = os.getenv(name) or os.getenv(name.lower())
    if required and not value:
        if default is None:
            raise ValueError(f"Environment variable {name} is required but not found")
        return default
    return value or default

class Settings:
    """Application settings using direct environment variable access"""
    
    def __init__(self):
        # Telegram Bot
        self.telegram_bot_token = get_env_var('TELEGRAM_BOT_TOKEN')
        
        # Database
        self.neon_database_url = get_env_var('NEON_DATABASE_URL')
        
        # Vercel API
        self.vercel_api_url = get_env_var('VERCEL_API_URL')
        self.vercel_api_key = get_env_var('VERCEL_API_KEY', required=False)
        
        # Langdock API (replaces OpenAI)
        self.langdock_api_key = get_env_var('LANGDOCK_API_KEY', required=False)
        
        # Open Food Facts
        self.openfoodfacts_api_url = get_env_var('OPENFOODFACTS_API_URL', 
                                                "https://world.openfoodfacts.org/api", 
                                                required=False)
        
        # Railway
        self.railway_environment = get_env_var('RAILWAY_ENVIRONMENT', "development", required=False)
        self.port = int(get_env_var('PORT', "8000", required=False))
        
        # Logging
        self.log_level = get_env_var('LOG_LEVEL', "INFO", required=False)
        
        # Rate Limiting
        self.rate_limit_requests = int(get_env_var('RATE_LIMIT_REQUESTS', "30", required=False))
        self.rate_limit_window = int(get_env_var('RATE_LIMIT_WINDOW', "60", required=False))
        
        # Cache
        self.cache_ttl = int(get_env_var('CACHE_TTL', "3600", required=False))
        self.max_cache_size = int(get_env_var('MAX_CACHE_SIZE', "1000", required=False))
        
        # Image Processing
        self.max_image_size = int(get_env_var('MAX_IMAGE_SIZE', "10485760", required=False))  # 10MB
        allowed_types_str = get_env_var('ALLOWED_IMAGE_TYPES', "jpg,jpeg,png,webp", required=False)
        self.allowed_image_types = [t.strip() for t in allowed_types_str.split(',')]
        
        # Health Check
        self.health_check_interval = int(get_env_var('HEALTH_CHECK_INTERVAL', "300", required=False))
        
        # Validate critical settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate critical settings"""
        if not self.telegram_bot_token or len(self.telegram_bot_token) < 10:
            raise ValueError('Invalid Telegram bot token')
        
        if not self.neon_database_url or not self.neon_database_url.startswith('postgresql'):
            raise ValueError('Invalid Neon database URL')
        
        if not self.vercel_api_url or not self.vercel_api_url.startswith('http'):
            raise ValueError('Invalid Vercel API URL')


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
