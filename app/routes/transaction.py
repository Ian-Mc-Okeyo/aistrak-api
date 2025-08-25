from fastapi import APIRouter, Request, HTTPException, Depends
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.crud.mpesa import MpesaGateWay
from app.crud.transaction import check_mpesa_txn_status

router = APIRouter()
mpesa_gateway = MpesaGateWay()

# mpesa callback
@router.post("/mpesa/callback")
async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    print(payload)
    response = mpesa_gateway.handle_callback(db, payload)
    if response:
        return {"status": "success", "data": response}
    raise HTTPException(status_code=400, detail="Invalid callback data")

@router.get("/mpesa/status/{reference}")
async def mpesa_status(reference: str, db: Session = Depends(get_db)):
    status = check_mpesa_txn_status(db, reference)
    return {"status": "success", "transaction_status": status}
