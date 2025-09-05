"""
Database service for managing user data and food logs
"""
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import db_manager, retry_db_operation
from models.db_models import User, FoodLog, ProductCache, UserSession

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations"""
    
    @retry_db_operation(max_retries=3)
    async def create_or_get_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "en"
    ) -> User:
        """Create new user or get existing one"""
        async with db_manager.get_session() as session:
            # Try to get existing user
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                # Update user info if changed
                updated = False
                if username and user.username != username:
                    user.username = username
                    updated = True
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                    updated = True
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                    updated = True
                
                if updated:
                    user.last_activity = datetime.utcnow()
                    await session.commit()
                
                return user
            
            # Create new user
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code,
                last_activity=datetime.utcnow()
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            logger.info(f"Created new user: {telegram_id}")
            return user
    
    @retry_db_operation(max_retries=2)
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by telegram ID"""
        async with db_manager.get_session() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    @retry_db_operation(max_retries=2)
    async def update_user_goal(self, telegram_id: int, calories: int) -> bool:
        """Update user's daily calorie goal"""
        try:
            async with db_manager.get_session() as session:
                stmt = (
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(
                        daily_goal_calories=calories,
                        updated_at=datetime.utcnow()
                    )
                )
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating user goal: {e}")
            return False
    
    @retry_db_operation(max_retries=2)
    async def update_user_language(self, telegram_id: int, language_code: str) -> bool:
        """Update user's language preference"""
        try:
            async with db_manager.get_session() as session:
                stmt = (
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(
                        language_code=language_code,
                        updated_at=datetime.utcnow()
                    )
                )
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating user language: {e}")
            return False
    
    @retry_db_operation(max_retries=3)
    async def add_food_log(
        self,
        user_id: int,
        product_name: str,
        quantity_g: float,
        calories: float,
        proteins: float,
        fats: float,
        carbs: float,
        source: str,
        brand: Optional[str] = None,
        barcode: Optional[str] = None,
        confidence_score: Optional[float] = None,
        meal_type: Optional[str] = None,
        notes: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> FoodLog:
        """Add new food log entry"""
        async with db_manager.get_session() as session:
            food_log = FoodLog(
                user_id=user_id,
                product_name=product_name,
                brand=brand,
                barcode=barcode,
                quantity_g=quantity_g,
                calories=calories,
                proteins=proteins,
                fats=fats,
                carbs=carbs,
                source=source,
                confidence_score=confidence_score,
                meal_type=meal_type,
                notes=notes,
                image_url=image_url
            )
            
            session.add(food_log)
            await session.commit()
            await session.refresh(food_log)
            
            logger.info(f"Added food log: {product_name} for user {user_id}")
            return food_log
    
    @retry_db_operation(max_retries=2)
    async def get_daily_nutrition_summary(self, user_id: int, target_date: date) -> Dict[str, float]:
        """Get nutrition summary for a specific date"""
        async with db_manager.get_session() as session:
            stmt = (
                select(
                    func.sum(FoodLog.calories).label('total_calories'),
                    func.sum(FoodLog.proteins).label('total_proteins'),
                    func.sum(FoodLog.fats).label('total_fats'),
                    func.sum(FoodLog.carbs).label('total_carbs'),
                    func.count(FoodLog.id).label('entries_count')
                )
                .where(
                    and_(
                        FoodLog.user_id == user_id,
                        FoodLog.date == target_date
                    )
                )
            )
            
            result = await session.execute(stmt)
            row = result.first()
            
            return {
                'calories': float(row.total_calories or 0),
                'proteins': float(row.total_proteins or 0),
                'fats': float(row.total_fats or 0),
                'carbs': float(row.total_carbs or 0),
                'entries_count': int(row.entries_count or 0)
            }
    
    @retry_db_operation(max_retries=2)
    async def get_weekly_nutrition_summary(self, user_id: int) -> Dict[str, float]:
        """Get nutrition summary for the last 7 days"""
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        async with db_manager.get_session() as session:
            stmt = (
                select(
                    func.sum(FoodLog.calories).label('total_calories'),
                    func.sum(FoodLog.proteins).label('total_proteins'),
                    func.sum(FoodLog.fats).label('total_fats'),
                    func.sum(FoodLog.carbs).label('total_carbs'),
                    func.count(FoodLog.id).label('entries_count')
                )
                .where(
                    and_(
                        FoodLog.user_id == user_id,
                        FoodLog.date >= start_date,
                        FoodLog.date <= end_date
                    )
                )
            )
            
            result = await session.execute(stmt)
            row = result.first()
            
            return {
                'calories': float(row.total_calories or 0),
                'proteins': float(row.total_proteins or 0),
                'fats': float(row.total_fats or 0),
                'carbs': float(row.total_carbs or 0),
                'entries_count': int(row.entries_count or 0),
                'days': 7
            }
    
    @retry_db_operation(max_retries=2)
    async def get_recent_food_logs(self, user_id: int, limit: int = 10) -> List[FoodLog]:
        """Get recent food logs for user"""
        async with db_manager.get_session() as session:
            stmt = (
                select(FoodLog)
                .where(FoodLog.user_id == user_id)
                .order_by(FoodLog.logged_at.desc())
                .limit(limit)
            )
            
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    @retry_db_operation(max_retries=2)
    async def get_daily_logs_count(self, user_id: int, target_date: date) -> int:
        """Get count of food logs for a specific date"""
        async with db_manager.get_session() as session:
            stmt = (
                select(func.count(FoodLog.id))
                .where(
                    and_(
                        FoodLog.user_id == user_id,
                        FoodLog.date == target_date
                    )
                )
            )
            
            result = await session.execute(stmt)
            return result.scalar() or 0
    
    @retry_db_operation(max_retries=3)
    async def clear_daily_logs(self, user_id: int, target_date: date) -> int:
        """Clear all food logs for a specific date"""
        async with db_manager.get_session() as session:
            stmt = (
                delete(FoodLog)
                .where(
                    and_(
                        FoodLog.user_id == user_id,
                        FoodLog.date == target_date
                    )
                )
            )
            
            result = await session.execute(stmt)
            await session.commit()
            
            deleted_count = result.rowcount
            logger.info(f"Deleted {deleted_count} food logs for user {user_id} on {target_date}")
            return deleted_count
    
    # Product Cache Methods
    
    @retry_db_operation(max_retries=2)
    async def get_cached_product_by_barcode(self, barcode: str) -> Optional[ProductCache]:
        """Get cached product by barcode"""
        async with db_manager.get_session() as session:
            stmt = select(ProductCache).where(ProductCache.barcode == barcode)
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()
            
            if product:
                # Update access statistics
                product.update_access()
                await session.commit()
            
            return product
    
    @retry_db_operation(max_retries=2)
    async def search_cached_products(self, query: str, limit: int = 10) -> List[ProductCache]:
        """Search cached products by name"""
        async with db_manager.get_session() as session:
            search_term = f"%{query.lower()}%"
            stmt = (
                select(ProductCache)
                .where(ProductCache.name.ilike(search_term))
                .order_by(ProductCache.access_count.desc())
                .limit(limit)
            )
            
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    @retry_db_operation(max_retries=3)
    async def cache_product(
        self,
        name: str,
        calories_per_100g: float,
        proteins_per_100g: float,
        fats_per_100g: float,
        carbs_per_100g: float,
        source: str,
        barcode: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        image_url: Optional[str] = None,
        data_quality_score: Optional[float] = None
    ) -> ProductCache:
        """Cache a product for future use"""
        async with db_manager.get_session() as session:
            # Check if product already exists
            if barcode:
                existing = await self.get_cached_product_by_barcode(barcode)
                if existing:
                    return existing
            
            product = ProductCache(
                barcode=barcode,
                name=name,
                brand=brand,
                calories_per_100g=calories_per_100g,
                proteins_per_100g=proteins_per_100g,
                fats_per_100g=fats_per_100g,
                carbs_per_100g=carbs_per_100g,
                category=category,
                image_url=image_url,
                source=source,
                data_quality_score=data_quality_score
            )
            
            session.add(product)
            await session.commit()
            await session.refresh(product)
            
            logger.info(f"Cached product: {name}")
            return product
    
    # Session Management
    
    @retry_db_operation(max_retries=2)
    async def get_user_session(self, telegram_id: int) -> Optional[UserSession]:
        """Get user session"""
        async with db_manager.get_session() as session:
            stmt = select(UserSession).where(UserSession.telegram_id == telegram_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    @retry_db_operation(max_retries=3)
    async def update_user_session(
        self,
        telegram_id: int,
        current_state: Optional[str] = None,
        session_data: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> UserSession:
        """Update or create user session"""
        async with db_manager.get_session() as session:
            # Try to get existing session
            stmt = select(UserSession).where(UserSession.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user_session = result.scalar_one_or_none()
            
            if user_session:
                # Update existing session
                if current_state is not None:
                    user_session.current_state = current_state
                if session_data is not None:
                    user_session.session_data = session_data
                if expires_at is not None:
                    user_session.expires_at = expires_at
                user_session.updated_at = datetime.utcnow()
            else:
                # Create new session
                user_session = UserSession(
                    telegram_id=telegram_id,
                    current_state=current_state,
                    session_data=session_data,
                    expires_at=expires_at
                )
                session.add(user_session)
            
            await session.commit()
            await session.refresh(user_session)
            return user_session
    
    @retry_db_operation(max_retries=2)
    async def cleanup_old_sessions(self, days_old: int = 7) -> int:
        """Clean up old expired sessions"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        async with db_manager.get_session() as session:
            stmt = (
                delete(UserSession)
                .where(
                    or_(
                        UserSession.expires_at < datetime.utcnow(),
                        UserSession.updated_at < cutoff_date
                    )
                )
            )
            
            result = await session.execute(stmt)
            await session.commit()
            
            deleted_count = result.rowcount
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old sessions")
            
            return deleted_count
    
    # Health Check
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            async with db_manager.get_session() as session:
                await session.execute(select(1))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    # Statistics and Analytics
    
    @retry_db_operation(max_retries=2)
    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        async with db_manager.get_session() as session:
            # Total entries
            total_entries_stmt = (
                select(func.count(FoodLog.id))
                .where(FoodLog.user_id == user_id)
            )
            total_entries = await session.scalar(total_entries_stmt) or 0
            
            # Days with entries
            days_with_entries_stmt = (
                select(func.count(func.distinct(FoodLog.date)))
                .where(FoodLog.user_id == user_id)
            )
            days_with_entries = await session.scalar(days_with_entries_stmt) or 0
            
            # Average daily calories (last 30 days)
            thirty_days_ago = date.today() - timedelta(days=30)
            avg_calories_stmt = (
                select(func.avg(func.sum(FoodLog.calories)))
                .where(
                    and_(
                        FoodLog.user_id == user_id,
                        FoodLog.date >= thirty_days_ago
                    )
                )
                .group_by(FoodLog.date)
            )
            avg_daily_calories = await session.scalar(avg_calories_stmt) or 0
            
            # Most logged products
            top_products_stmt = (
                select(
                    FoodLog.product_name,
                    func.count(FoodLog.id).label('count'),
                    func.sum(FoodLog.quantity_g).label('total_quantity')
                )
                .where(FoodLog.user_id == user_id)
                .group_by(FoodLog.product_name)
                .order_by(func.count(FoodLog.id).desc())
                .limit(5)
            )
            top_products_result = await session.execute(top_products_stmt)
            top_products = [
                {
                    'name': row.product_name,
                    'count': row.count,
                    'total_quantity': float(row.total_quantity)
                }
                for row in top_products_result
            ]
            
            return {
                'total_entries': total_entries,
                'days_with_entries': days_with_entries,
                'avg_daily_calories': float(avg_daily_calories),
                'top_products': top_products
            }
