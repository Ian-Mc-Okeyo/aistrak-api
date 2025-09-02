from fastapi import APIRouter, Request, HTTPException, Depends
from app.crud.user import get_user_wallet, get_user_achievements
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.util import authenticate_and_get_user_details

router = APIRouter()

@router.get("/wallet")
def read_user_wallet(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details["user_id"]
    wallet = get_user_wallet(db, user_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"status": "success", "wallet": wallet}

@router.get("/achievements")
def read_user_achievements(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details["user_id"]
    achievements = get_user_achievements(db, user_id)
    return {"status": "success", "achievements": achievements}