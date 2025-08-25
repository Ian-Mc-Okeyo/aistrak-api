from sqlalchemy import Column, String, Boolean, DateTime, Float, Enum, ForeignKey, Integer, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from uuid import uuid4
from datetime import datetime
from app.core.database import Base
from app.models.token import Token
import enum

class AiPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    token_id = Column(String(36), ForeignKey("tokens.id"))
    target_timestamp = Column(DateTime, nullable=False)
    predicted_price = Column(Float, nullable=False)
    confidence_score = Column(Float)
    extra_data = Column(MySQLJSON)
    created_at = Column(DateTime, default=datetime.now)

    token = relationship("Token")

class MarketSentiment(Base):
    __tablename__ = "market_sentiment"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    token_id = Column(String(36), ForeignKey("tokens.id"))
    sentiment_score = Column(Float, nullable=False)
    bullish_percentage = Column(Integer)
    bearish_percentage = Column(Integer)
    neutral_percentage = Column(Integer)
    data_source = Column(String(50))
    timestamp = Column(DateTime, default=datetime.now)