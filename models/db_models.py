"""
Database models for the Nutrition Bot
"""
from datetime import datetime
from datetime import date as date_type
from typing import Optional, List
from sqlalchemy import (
    BigInteger,
    String,
    Integer,
    Float,
    DateTime,
    Date,
    Text,
    Index,
    UniqueConstraint,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from config.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # User preferences
    daily_goal_calories: Mapped[int] = mapped_column(Integer, default=2000)
    daily_goal_proteins: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    daily_goal_fats: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    daily_goal_carbs: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Settings
    language_code: Mapped[str] = mapped_column(String(10), default="en")
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    notifications_enabled: Mapped[bool] = mapped_column(default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Relationships
    food_logs: Mapped[List["FoodLog"]] = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"
    
    @property
    def display_name(self) -> str:
        """Get user display name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        else:
            return f"User {self.telegram_id}"


class FoodLog(Base):
    """Food log entry model"""
    __tablename__ = "food_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Product information
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Quantity and nutrition
    quantity_g: Mapped[float] = mapped_column(Float, nullable=False)
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    proteins: Mapped[float] = mapped_column(Float, nullable=False)
    fats: Mapped[float] = mapped_column(Float, nullable=False)
    carbs: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Additional nutrition info (optional)
    fiber: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sugar: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sodium: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Source and metadata
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # 'search', 'barcode', 'photo'
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # For AI analysis
    meal_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # breakfast, lunch, dinner, snack
    
    # Timestamps
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    date: Mapped[date] = mapped_column(Date, default=func.current_date(), index=True)
    
    # Additional data (JSON-like storage for flexibility)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="food_logs")
    
    # Constraints
    __table_args__ = (
        Index("idx_food_logs_user_date", "user_id", "date"),
        Index("idx_food_logs_source", "source"),
        Index("idx_food_logs_barcode", "barcode"),
        CheckConstraint("quantity_g > 0", name="check_positive_quantity"),
        CheckConstraint("calories >= 0", name="check_non_negative_calories"),
        CheckConstraint("proteins >= 0", name="check_non_negative_proteins"),
        CheckConstraint("fats >= 0", name="check_non_negative_fats"),
        CheckConstraint("carbs >= 0", name="check_non_negative_carbs"),
    )
    
    def __repr__(self) -> str:
        return f"<FoodLog(id={self.id}, user_id={self.user_id}, product={self.product_name}, quantity={self.quantity_g}g)>"
    
    @property
    def calories_per_100g(self) -> float:
        """Calculate calories per 100g"""
        return (self.calories / self.quantity_g) * 100 if self.quantity_g > 0 else 0
    
    @property
    def proteins_per_100g(self) -> float:
        """Calculate proteins per 100g"""
        return (self.proteins / self.quantity_g) * 100 if self.quantity_g > 0 else 0
    
    @property
    def fats_per_100g(self) -> float:
        """Calculate fats per 100g"""
        return (self.fats / self.quantity_g) * 100 if self.quantity_g > 0 else 0
    
    @property
    def carbs_per_100g(self) -> float:
        """Calculate carbs per 100g"""
        return (self.carbs / self.quantity_g) * 100 if self.quantity_g > 0 else 0


class ProductCache(Base):
    """Product cache model for frequently accessed products"""
    __tablename__ = "products_cache"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Product identifiers
    barcode: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Nutrition per 100g
    calories_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    proteins_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    fats_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_per_100g: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Additional nutrition (optional)
    fiber_per_100g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sugar_per_100g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sodium_per_100g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Product metadata
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # 'openfoodfacts', 'manual', etc.
    
    # Cache metadata
    cached_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    access_count: Mapped[int] = mapped_column(Integer, default=1)
    last_accessed: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Quality indicators
    data_quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    
    # Constraints
    __table_args__ = (
        Index("idx_products_cache_name", "name"),
        Index("idx_products_cache_brand", "brand"),
        Index("idx_products_cache_category", "category"),
        CheckConstraint("calories_per_100g >= 0", name="check_non_negative_calories_cache"),
        CheckConstraint("proteins_per_100g >= 0", name="check_non_negative_proteins_cache"),
        CheckConstraint("fats_per_100g >= 0", name="check_non_negative_fats_cache"),
        CheckConstraint("carbs_per_100g >= 0", name="check_non_negative_carbs_cache"),
        CheckConstraint("access_count >= 0", name="check_non_negative_access_count"),
    )
    
    def __repr__(self) -> str:
        return f"<ProductCache(id={self.id}, name={self.name}, barcode={self.barcode})>"
    
    def calculate_nutrition(self, quantity_g: float) -> dict:
        """Calculate nutrition for given quantity"""
        multiplier = quantity_g / 100.0
        return {
            "calories": self.calories_per_100g * multiplier,
            "proteins": self.proteins_per_100g * multiplier,
            "fats": self.fats_per_100g * multiplier,
            "carbs": self.carbs_per_100g * multiplier,
            "fiber": self.fiber_per_100g * multiplier if self.fiber_per_100g else None,
            "sugar": self.sugar_per_100g * multiplier if self.sugar_per_100g else None,
            "sodium": self.sodium_per_100g * multiplier if self.sodium_per_100g else None,
        }
    
    def update_access(self) -> None:
        """Update access statistics"""
        self.access_count += 1
        self.last_accessed = func.now()


class UserSession(Base):
    """User session model for tracking user states"""
    __tablename__ = "user_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    
    # Session data
    current_state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    session_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON data
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("telegram_id", name="uq_user_sessions_telegram_id"),
        Index("idx_user_sessions_state", "current_state"),
    )
    
    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, telegram_id={self.telegram_id}, state={self.current_state})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


# Create indexes for better performance
def create_additional_indexes():
    """Create additional indexes for performance optimization"""
    indexes = [
        # User indexes
        Index("idx_users_telegram_id", User.telegram_id),
        Index("idx_users_username", User.username),
        Index("idx_users_last_activity", User.last_activity),
        
        # Food log indexes
        Index("idx_food_logs_user_date_meal", FoodLog.user_id, FoodLog.date, FoodLog.meal_type),
        Index("idx_food_logs_logged_at", FoodLog.logged_at),
        Index("idx_food_logs_product_name", FoodLog.product_name),
        
        # Product cache indexes
        Index("idx_products_cache_access_count", ProductCache.access_count.desc()),
        Index("idx_products_cache_last_accessed", ProductCache.last_accessed.desc()),
        Index("idx_products_cache_quality", ProductCache.data_quality_score.desc()),
    ]
    return indexes
