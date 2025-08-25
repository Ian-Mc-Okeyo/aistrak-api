from sqlalchemy import Column, String, Boolean, DateTime, Float, Enum, ForeignKey, Integer, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from uuid import uuid4
from datetime import datetime
from app.core.database import Base
from app.models.token import Token
import enum

class ResolutionMethod(enum.Enum):
    exact = "exact"
    threshold = "threshold"
    range = "range"
    percent_delta = "percent_delta"


class PaymentMethod(enum.Enum):
    mpesa = "mpesa"
    usdt = "usdt"
    internal = "internal"


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    token_id = Column(String(36), ForeignKey("tokens.id"), nullable=False)
    target_timestamp = Column(DateTime, nullable=False)
    predicted_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    confidence = Column(Float)
    stake_amount = Column(Float, nullable=False)
    result = Column(Enum("Pending", "Correct", "Incorrect", name="prediction_result"), default="Pending")
    resolution_timestamp = Column(DateTime)
    resolution_method = Column(Enum(ResolutionMethod), default=ResolutionMethod.exact)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.internal)
    payment_reference = Column(String(100), nullable=True) # for mpesa
    payment_status = Column(Enum("Pending", "Complete", "Failed", name="payment_status"), default="Pending")
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="predictions")
    token = relationship("Token")
