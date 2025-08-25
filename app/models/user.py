from sqlalchemy import Column, String, Boolean, DateTime, Float, Enum, ForeignKey, Integer, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from uuid import uuid4
from datetime import datetime
from app.core.database import Base
from app.models.prediction import Prediction
from app.models.wallet import UserWallet
import enum

class AuthType(enum.Enum):
    email = "email"
    wallet = "wallet"

class AchievementType(enum.Enum):
    first_prediction = "first_prediction"
    accuracy_master = "accuracy_master"
    high_roller = "high_roller"
    streak_master = "streak_master"
    community_leader = "community_leader"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(250), unique=True, nullable=True)
    username = Column(String(250), unique=True, nullable=True)
    first_name = Column(String(200), nullable=True)
    last_name = Column(String(200), nullable=True)
    wallet_address = Column(String(255), unique=True, nullable=True)
    phone_number = Column(String(20), nullable=True)
    auth_type = Column(Enum(AuthType), nullable=False)
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = Column(DateTime)

    predictions = relationship("Prediction", back_populates="user")
    wallet = relationship("UserWallet", back_populates="user", uselist=False)

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    achievement_type = Column(Enum(AchievementType), nullable=False)
    earned_at = Column(DateTime, default=datetime.now)

class UserSetting(Base):
    __tablename__ = "user_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    prediction_reminders = Column(Boolean, default=False)
    public_profile = Column(Boolean, default=True)
    show_prediction_history = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)