from fastapi import APIRouter, Request, HTTPException, Depends
from app.core.database import get_db
from app.schemas.prediction import CreateMpesaPrediction
from sqlalchemy.orm import Session
from app.crud.prediction import create_mpesa_prediction, count_active_predictions, get_total_staked_amount, get_predictions_with_details
from app.util import authenticate_and_get_user_details

router = APIRouter()

@router.post("/create")
def create_mpesa_prediction_router(request: Request, prediction: CreateMpesaPrediction, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details["user_id"]
    prediction = create_mpesa_prediction(db, user_id, prediction)

    return {"status": "Success", "reference": prediction.payment_reference}

@router.get("/user/active")
def count_active_predictions_router(request: Request, db: Session = Depends(get_db)):
    user_details = authenticate_and_get_user_details(request)
    user_id = user_details["user_id"]
    count = count_active_predictions(db, user_id)
    total_staked = get_total_staked_amount(db, user_id)
    return {"status": "Success", "active_count": count, "total_staked": total_staked}

@router.get("/list")
def get_predictions_list_router(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    authenticate_and_get_user_details(request)
    predictions = get_predictions_with_details(db, skip=skip, limit=limit)
    return {"status": "Success", "predictions": predictions}
