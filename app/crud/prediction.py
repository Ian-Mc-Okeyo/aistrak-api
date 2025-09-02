from app.models.prediction import Prediction
from app.models.transaction import Transaction
from app.models.token import Token
from app.models.user import User, UserWallet, UserAchievement
from datetime import datetime
from app.core.database import Base
from sqlalchemy.orm import Session
from app.schemas.prediction import CreateMpesaPrediction
from app.crud.mpesa import MpesaGateWay
import random
import string
from fastapi import HTTPException
from sqlalchemy import func

mpesa_gateway = MpesaGateWay()

def random_10_letter_string():
    return ''.join(random.choices(string.ascii_letters, k=10))

def create_mpesa_prediction(db: Session, user_id: str, prediction: CreateMpesaPrediction):
    # user and token must exist
    user = db.query(User).filter(User.id == user_id).first()
    token = db.query(Token).filter(Token.id == prediction.token_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    db_prediction = Prediction(
        user_id=user_id,
        token_id=prediction.token_id,
        target_timestamp=prediction.target_timestamp,
        predicted_price=prediction.predicted_price,
        stake_amount=prediction.stake_amount,
        confidence=prediction.confidence,
        payment_method=prediction.payment_method,
        payment_reference = random_10_letter_string(),
        current_price = 289 # to be done
    )

    # create the internal transaction
    internal_tx = Transaction(
        user_id=user_id,
        amount=prediction.stake_amount,
        tx_type="Stake",
        status="Pending",
        payment_method=prediction.payment_method,
        tx_hash=db_prediction.payment_reference
    )

    db.add(internal_tx)
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)

    if prediction.payment_method == "mpesa" and prediction.phone_number:

        mpesa_gateway.stk_push_request(
            db=db,
            phone_number=prediction.phone_number,
            amount=prediction.stake_amount + prediction.fee,
            reference=db_prediction.payment_reference
        )

    return db_prediction

# count the number of active predictions of a user
def count_active_predictions(db: Session, user_id: str):
    return db.query(Prediction).filter(
        Prediction.user_id == user_id,
        Prediction.result == "Pending"
    ).count()

# get total amount staked that are active
def get_total_staked_amount(db: Session, user_id: str):
    return db.query(Prediction).filter(
        Prediction.user_id == user_id,
        Prediction.result == "Pending"
    ).with_entities(func.sum(Prediction.stake_amount)).scalar() or 0

# get a list of all predictions with a limit of 100
def get_predictions_with_details(db: Session, skip: int = 0, limit: int = 100):
    results = (
        db.query(
            Prediction.id.label("prediction_id"),
            Prediction.target_timestamp,
            Prediction.stake_amount,
            Prediction.confidence,
            Prediction.result,
            Prediction.predicted_price,
            Prediction.current_price,
            User.id.label("user_id"),
            User.username,
            Token.id.label("token_id"),
            Token.symbol.label("token_symbol"),
            Token.name.label("token_name"),
        )
        .join(User, Prediction.user_id == User.id)
        .join(Token, Prediction.token_id == Token.id)
        .order_by(Prediction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [dict(row._mapping) for row in results]

# get user predictions
def get_user_predictions(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    results = (
        db.query(
            Prediction.id.label("prediction_id"),
            Prediction.target_timestamp,
            Prediction.stake_amount,
            Prediction.confidence,
            Prediction.result,
            Prediction.predicted_price,
            Prediction.reward,
            Prediction.current_price,
            Token.id.label("token_id"),
            Token.symbol.label("token_symbol"),
            Token.name.label("token_name"),
        )
        # .join(User, Prediction.user_id == User.id)  # Remove this line
        .join(Token, Prediction.token_id == Token.id)
        .filter(Prediction.user_id == user_id)
        .order_by(Prediction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [dict(row._mapping) for row in results]