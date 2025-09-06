"""
Database configuration and connection management
"""
import asyncio
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from sqlalchemy import event

from config.settings import DATABASE_CONFIG

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
    
    async def initialize(self) -> None:
        """Initialize database connection"""
        try:
            # Ensure the database URL uses asyncpg driver
            db_url = DATABASE_CONFIG["url"]
            if db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif not db_url.startswith("postgresql+asyncpg://"):
                # If it's already postgresql+asyncpg://, keep it as is
                pass
            
            self._engine = create_async_engine(
                db_url,
                echo=DATABASE_CONFIG["echo"],
                pool_size=DATABASE_CONFIG["pool_size"],
                max_overflow=DATABASE_CONFIG["max_overflow"],
                pool_timeout=DATABASE_CONFIG["pool_timeout"],
                pool_recycle=DATABASE_CONFIG["pool_recycle"],
                poolclass=NullPool if "railway" in db_url else None,
            )
            
            # Add connection event listeners
            @event.listens_for(self._engine.sync_engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                if "sqlite" in DATABASE_CONFIG["url"]:
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
            
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            # Test connection
            async with self._engine.begin() as conn:
                await conn.execute("SELECT 1")
            
            logger.info("Database connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self) -> None:
        """Close database connection"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connection closed")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session context manager"""
        if not self._session_factory:
            raise RuntimeError("Database not initialized")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def get_session_direct(self) -> AsyncSession:
        """Get database session directly (for dependency injection)"""
        if not self._session_factory:
            raise RuntimeError("Database not initialized")
        return self._session_factory()
    
    @property
    def engine(self) -> AsyncEngine:
        """Get database engine"""
        if not self._engine:
            raise RuntimeError("Database not initialized")
        return self._engine
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            async with self.get_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


async def init_database() -> None:
    """Initialize database connection"""
    await db_manager.initialize()


async def close_database() -> None:
    """Close database connection"""
    await db_manager.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async with db_manager.get_session() as session:
        yield session


async def create_tables() -> None:
    """Create all database tables"""
    try:
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


async def drop_tables() -> None:
    """Drop all database tables (for testing)"""
    try:
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


class DatabaseHealthCheck:
    """Database health check utility"""
    
    @staticmethod
    async def check_connection() -> dict:
        """Check database connection status"""
        try:
            is_healthy = await db_manager.health_check()
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "database": "connected" if is_healthy else "disconnected",
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "error",
                "error": str(e),
            }
    
    @staticmethod
    async def check_tables() -> dict:
        """Check if required tables exist"""
        try:
            async with db_manager.get_session() as session:
                # Check if main tables exist
                tables_to_check = ["users", "food_logs", "products_cache"]
                existing_tables = []
                
                for table in tables_to_check:
                    try:
                        await session.execute(f"SELECT 1 FROM {table} LIMIT 1")
                        existing_tables.append(table)
                    except Exception:
                        pass
                
                return {
                    "status": "healthy" if len(existing_tables) == len(tables_to_check) else "partial",
                    "tables": existing_tables,
                    "missing": list(set(tables_to_check) - set(existing_tables)),
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }


# Connection retry decorator
def retry_db_operation(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying database operations"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Database operation failed (attempt {attempt + 1}): {e}")
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"Database operation failed after {max_retries} attempts: {e}")
            
            raise last_exception
        return wrapper
    return decorator
