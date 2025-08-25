from sqlalchemy import Column, String, Boolean, DateTime, Float, Enum, ForeignKey, Integer, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from uuid import uuid4
from datetime import datetime
from app.core.database import Base
import enum

class WithdrawalMethod(enum.Enum):
    USDT = "USDT"
    MPESA = "MPESA"

class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    withdrawal_method = Column(Enum(WithdrawalMethod), nullable=False)
    wallet_address = Column(String(42), nullable=True)
    phone_number = Column(String(20), nullable=True)
    status = Column(Enum("pending", "processing", "completed", "failed", name="withdrawal_status"), default="pending")
    transaction_hash = Column(String(66), nullable=True)
    mpesa_receipt = Column(String(50), nullable=True)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)