from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateMpesaPrediction(BaseModel):
    token_id: str
    target_timestamp: datetime
    predicted_price: float
    stake_amount: float
    confidence: Optional[float] = None
    payment_method: Optional[str] = "internal"  # Default to internal payment method
    phone_number: Optional[str] = None
    txn_hash: Optional[str] = None
    fee: Optional[float] = 0.0  # Optional fee for the prediction
    class Config:
        orm_mode = True