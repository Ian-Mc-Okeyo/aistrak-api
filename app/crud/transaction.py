from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.transaction import MpesaTransaction

# Check Mpesa Transaction status
def check_mpesa_txn_status(db: Session, reference: str):
    mpesa_tx = db.query(MpesaTransaction).filter_by(reference=reference).first()
    if not mpesa_tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return mpesa_tx.status