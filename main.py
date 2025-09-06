"""
Main entry point for the Nutrition Bot
"""
import asyncio
import logging
import logging.config
import os
import signal
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from config.settings import settings, BOT_CONFIG, LOGGING_CONFIG
from config.database import init_database, close_database, create_tables
from handlers import register_all_handlers
from services.database_service import DatabaseService
from utils.cache import CacheManager
from utils.rate_limiter import AdvancedRateLimiter
from utils.middleware import setup_middlewares

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class NutritionBot:
    """Main bot application class"""
    
    def __init__(self):
        self.bot: Bot = None
        self.dp: Dispatcher = None
        self.app: web.Application = None
        self.db_service: DatabaseService = None
        self.cache_manager: CacheManager = None
        self.rate_limiter: AdvancedRateLimiter = None
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self) -> None:
        """Initialize bot components with emergency fallback mode"""
        logger.info("Initializing Nutrition Bot...")
        
        # Emergency mode flag
        emergency_mode = False
        
        try:
            # Try to initialize database with aggressive timeout
            logger.info("🔄 Attempting database initialization...")
            
            # Set shorter timeout for database operations
            import asyncio
            try:
                await asyncio.wait_for(init_database(), timeout=10.0)
                await asyncio.wait_for(create_tables(), timeout=10.0)
                logger.info("✅ Database initialized successfully")
            except asyncio.TimeoutError:
                logger.error("⏰ Database initialization timeout - entering EMERGENCY MODE")
                emergency_mode = True
            except Exception as db_error:
                logger.error(f"💥 Database initialization failed: {db_error} - entering EMERGENCY MODE")
                emergency_mode = True
            
            # Initialize services (always succeed)
            logger.info("🔄 Initializing services...")
            self.db_service = DatabaseService()
            self.cache_manager = CacheManager()
            self.rate_limiter = AdvancedRateLimiter()
            
            # Initialize bot and dispatcher (critical - must succeed)
            logger.info("🔄 Initializing bot and dispatcher...")
            self.bot = Bot(
                token=BOT_CONFIG["token"],
                parse_mode=ParseMode.HTML
            )
            
            self.dp = Dispatcher(storage=MemoryStorage())
            
            # Setup middlewares (with emergency mode flag)
            logger.info("🔄 Setting up middlewares...")
            setup_middlewares(self.dp, self.db_service, self.cache_manager, self.rate_limiter)
            
            # Register handlers
            logger.info("🔄 Registering handlers...")
            register_all_handlers(self.dp)
            
            # Create web application for health checks
            self.app = web.Application()
            self.setup_routes()
            
            if emergency_mode:
                logger.warning("🚨 BOT STARTED IN EMERGENCY MODE - Database unavailable, using fallbacks")
                logger.warning("🔧 Features available: Text search with offline DB, Basic commands")
                logger.warning("🚫 Features limited: Database logging, User statistics, History")
            else:
                logger.info("✅ Bot initialized successfully in FULL MODE")
            
        except Exception as e:
            logger.error(f"💥 CRITICAL: Failed to initialize bot core components: {e}")
            logger.error("🆘 Attempting minimal emergency initialization...")
            
            # Last resort emergency initialization
            try:
                self.bot = Bot(token=BOT_CONFIG["token"], parse_mode=ParseMode.HTML)
                self.dp = Dispatcher(storage=MemoryStorage())
                self.app = web.Application()
                self.setup_routes()
                
                # Register only basic handlers without middleware
                from handlers.basic import router as basic_router
                self.dp.include_router(basic_router)
                
                logger.warning("🆘 MINIMAL EMERGENCY MODE - Only basic commands available")
                
            except Exception as critical_error:
                logger.error(f"💀 FATAL: Cannot initialize even minimal bot: {critical_error}")
                raise
    
    def setup_routes(self) -> None:
        """Setup web application routes"""
        self.app.router.add_get("/health", self.health_check)
        self.app.router.add_get("/", self.root_handler)
    
    async def health_check(self, request: Request) -> Response:
        """Health check endpoint"""
        try:
            # Check database connection
            db_healthy = await self.db_service.health_check()
            
            # Check bot connection
            bot_info = await self.bot.get_me()
            bot_healthy = bool(bot_info)
            
            status = "healthy" if (db_healthy and bot_healthy) else "unhealthy"
            
            health_data = {
                "status": status,
                "database": "connected" if db_healthy else "disconnected",
                "bot": "connected" if bot_healthy else "disconnected",
                "bot_username": bot_info.username if bot_info else None,
                "timestamp": asyncio.get_event_loop().time(),
            }
            
            return web.json_response(
                health_data,
                status=200 if status == "healthy" else 503
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return web.json_response(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": asyncio.get_event_loop().time(),
                },
                status=503
            )
    
    async def root_handler(self, request: Request) -> Response:
        """Root endpoint handler"""
        return web.json_response({
            "service": "Nutrition Bot",
            "version": "1.0.0",
            "status": "running",
        })
    
    async def start_polling(self) -> None:
        """Start bot in polling mode"""
        logger.info("Starting bot in polling mode...")
        
        try:
            # Start background tasks
            asyncio.create_task(self._background_tasks())
            
            # Start polling
            await self.dp.start_polling(
                self.bot,
                allowed_updates=self.dp.resolve_used_update_types()
            )
            
        except Exception as e:
            logger.error(f"Error in polling mode: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def start_webhook(self, webhook_url: str, webhook_path: str = "/webhook") -> None:
        """Start bot in webhook mode"""
        logger.info(f"Starting bot in webhook mode: {webhook_url}")
        
        try:
            # Setup webhook handler BEFORE starting server
            webhook_requests_handler = SimpleRequestHandler(
                dispatcher=self.dp,
                bot=self.bot,
            )
            webhook_requests_handler.register(self.app, path=webhook_path)
            logger.info(f"Webhook handler registered for path: {webhook_path}")
            
            # Start web server
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, host="0.0.0.0", port=settings.port)
            await site.start()
            
            logger.info(f"Webhook server started on port {settings.port} - Updated with fixes")
            
            # Set webhook AFTER server is running
            await self.bot.set_webhook(
                url=f"{webhook_url}{webhook_path}",
                allowed_updates=self.dp.resolve_used_update_types()
            )
            logger.info(f"Webhook set to: {webhook_url}{webhook_path}")
            
            # Start background tasks
            asyncio.create_task(self._background_tasks())
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Error in webhook mode: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def start_server_only(self) -> None:
        """Start only web server (for health checks)"""
        logger.info("Starting web server only...")
        
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, host="0.0.0.0", port=settings.port)
            await site.start()
            
            logger.info(f"Web server started on port {settings.port}")
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Error starting web server: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def _background_tasks(self) -> None:
        """Run background maintenance tasks with error isolation"""
        logger.info("Starting background tasks...")
        
        while not self._shutdown_event.is_set():
            try:
                # Cache cleanup (safe operation)
                try:
                    if self.cache_manager:
                        await self.cache_manager.cleanup_expired()
                except Exception as e:
                    logger.warning(f"Cache cleanup failed (non-critical): {e}")
                
                # Database maintenance (with timeout and fallback)
                try:
                    if self.db_service:
                        await asyncio.wait_for(
                            self.db_service.cleanup_old_sessions(), 
                            timeout=30.0
                        )
                except asyncio.TimeoutError:
                    logger.warning("Database cleanup timeout (non-critical)")
                except Exception as e:
                    logger.warning(f"Database cleanup failed (non-critical): {e}")
                
                # Rate limiter cleanup (safe operation)
                try:
                    if self.rate_limiter:
                        self.rate_limiter.cleanup()
                except Exception as e:
                    logger.warning(f"Rate limiter cleanup failed (non-critical): {e}")
                
                # Wait before next cleanup
                await asyncio.sleep(300)  # 5 minutes
                
            except asyncio.CancelledError:
                logger.info("Background tasks cancelled")
                break
            except Exception as e:
                logger.error(f"Unexpected error in background tasks: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def cleanup(self) -> None:
        """Cleanup resources with error isolation"""
        logger.info("Cleaning up resources...")
        
        # Bot session cleanup
        try:
            if self.bot:
                await asyncio.wait_for(self.bot.session.close(), timeout=5.0)
                logger.info("✅ Bot session closed")
        except asyncio.TimeoutError:
            logger.warning("⏰ Bot session close timeout (non-critical)")
        except Exception as e:
            logger.warning(f"⚠️ Bot session close failed (non-critical): {e}")
        
        # Cache manager cleanup
        try:
            if self.cache_manager:
                await asyncio.wait_for(self.cache_manager.close(), timeout=5.0)
                logger.info("✅ Cache manager closed")
        except asyncio.TimeoutError:
            logger.warning("⏰ Cache manager close timeout (non-critical)")
        except Exception as e:
            logger.warning(f"⚠️ Cache manager close failed (non-critical): {e}")
        
        # Database cleanup
        try:
            await asyncio.wait_for(close_database(), timeout=10.0)
            logger.info("✅ Database connection closed")
        except asyncio.TimeoutError:
            logger.warning("⏰ Database close timeout (non-critical)")
        except Exception as e:
            logger.warning(f"⚠️ Database close failed (non-critical): {e}")
        
        logger.info("🧹 Cleanup completed (with graceful error handling)")
    
    def shutdown(self) -> None:
        """Signal shutdown"""
        logger.info("Shutdown signal received")
        self._shutdown_event.set()


# Global bot instance
nutrition_bot = NutritionBot()


def setup_signal_handlers() -> None:
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        nutrition_bot.shutdown()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main() -> None:
    """Main application entry point"""
    setup_signal_handlers()
    
    try:
        await nutrition_bot.initialize()
        
        # EMERGENCY FIX: Force polling mode to make bot work
        # Webhook mode has issues with Railway, use polling for now
        force_polling = os.getenv('FORCE_POLLING_MODE', '').lower() == 'true'
        
        if force_polling:
            # Force polling mode - delete webhook first
            logger.info("🔄 EMERGENCY POLLING MODE - Forced by FORCE_POLLING_MODE")
            logger.info("🗑️ Deleting webhook to enable polling...")
            await nutrition_bot.bot.delete_webhook(drop_pending_updates=True)
            logger.info("✅ Webhook deleted, starting polling mode")
            await nutrition_bot.start_polling()
        else:
            # Try webhook mode first
            is_railway = (
                os.getenv('PORT') or 
                os.getenv('RAILWAY_PROJECT_ID') or 
                os.getenv('FORCE_WEBHOOK_MODE', '').lower() == 'true' or
                'railway.app' in os.getenv('RAILWAY_PUBLIC_DOMAIN', '') or
                'railway.app' in os.getenv('RAILWAY_STATIC_URL', '')
            )
            
            if is_railway:
                # Production mode - webhook (Railway)
                railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL', '').replace('https://', '') or 'nutrition-bot.railway.app'
                webhook_url = f"https://{railway_domain}"
                logger.info(f"🚀 STARTING WEBHOOK MODE - Railway detected")
                logger.info(f"📍 PORT: {os.getenv('PORT')}")
                logger.info(f"🔗 WEBHOOK URL: {webhook_url}")
                await nutrition_bot.start_webhook(webhook_url)
            else:
                # Development mode - polling
                logger.info("🔄 STARTING POLLING MODE - Local development")
                await nutrition_bot.start_polling()
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted")
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)
