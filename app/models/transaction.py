from sqlalchemy import Column, String, Boolean, DateTime, Float, Enum, ForeignKey, Integer, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from uuid import uuid4
from datetime import datetime
from app.core.database import Base
import enum

class PaymentMethod(enum.Enum):
    mpesa = "mpesa"
    usdt = "usdt"
    internal = "internal"

class TransactionStatusEnum(str, enum.Enum):
    pending = "Pending"
    complete = "Complete"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    tx_type = Column(Enum("Stake", "Reward", "Deposit", "Withdrawal", name="transaction_type"))
    status = Column(Enum("Pending", "Complete", "Failed", name="transaction_status"), default="Pending")
    payment_method = Column(Enum(PaymentMethod))
    tx_hash = Column(String(255), nullable=True)
    mpesa_receipt = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class MpesaTransaction(Base):
    __tablename__ = "mpesa_transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    transaction_no = Column(String(50), unique=True, default=lambda: str(uuid4()))
    phone_number = Column(String(20), nullable=False)
    checkout_request_id = Column(String(200), nullable=False)
    reference = Column(String(40), nullable=True)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(Enum(TransactionStatusEnum), default=TransactionStatusEnum.pending)
    receipt_no = Column(String(200), nullable=True)
    created = Column(DateTime, default=datetime.now)
    ip = Column(String(200), nullable=True)
    billref = Column(String(200), nullable=True)

    def __repr__(self):
        return f"<MpesaTransaction(transaction_no={self.transaction_no})>"
