import logging
import time
import os
import math
import base64
from datetime import datetime
import requests
import random
from sqlalchemy.orm import Session
from app.models.transaction import MpesaTransaction, Transaction
from app.models.prediction import Prediction
from app.models.user import UserAchievement
from app.models.wallet import UserWallet
from fastapi import HTTPException
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("default")

def complete_prediction_payment(db: Session, reference: str):
    # get the prediction
    prediction = db.query(Prediction).filter_by(payment_reference=reference).first()
    prediction.payment_status = "Complete"

    # update the wallet balance
    user_wallet = db.query(UserWallet).filter_by(user_id=prediction.user_id).first()
    if user_wallet:
        user_wallet.total_staked += prediction.stake_amount
        user_wallet.updated_at = datetime.now()

    # create the achievement for first prediction
    user_first_prediction = db.query(UserAchievement).filter_by(
        user_id=prediction.user_id,
        achievement_type="first_prediction"
    ).first()
    
    if not user_first_prediction:
        user_achievement = UserAchievement(
            user_id=prediction.user_id,
            achievement_type="first_prediction",
            earned_at=datetime.now(),
        )
        db.add(user_achievement)
    
    if user_wallet.total_staked >= 100:
        high_roller_achievement = db.query(UserAchievement).filter_by(
            user_id=prediction.user_id,
            achievement_type="high_roller"
        ).first()

        if not high_roller_achievement:
            user_achievement2 = UserAchievement(
                user_id=prediction.user_id,
                achievement_type="high_roller",
                earned_at=datetime.now(),
            )
            db.add(user_achievement2)

class MpesaGateWay:
    def __init__(self):
        self.shortcode = os.getenv("MPESA_EXPRESS_SHORTCODE")
        self.consumer_key = os.getenv("MPESA_CONSUMER_KEY")
        self.consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
        self.access_token_url = os.getenv("ACCESS_TOKEN_URL")
        self.billrefnumber = os.getenv("BILL_REF_NUMBER")
        self.password = self.generate_password()
        self.c2b_callback = os.getenv("C2B_CALLBACK")
        self.checkout_url = os.getenv("CHECKOUT_URL")
        self.access_token = self.get_access_token()
        self.access_token_expiration = time.time() + 3400
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def get_access_token(self):
        try:
            res = requests.get(
                self.access_token_url,
                auth=(self.consumer_key, self.consumer_secret),
            )
            res.raise_for_status()
        except Exception as err:
            print("Access Token")
            print(err)
            logger.error(f"Error getting access token: {err}")
            raise HTTPException(status_code=500, detail="Mpesa access token error")
        return res.json()["access_token"]

    def generate_password(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_str = os.getenv("MPESA_EXPRESS_SHORTCODE") + os.getenv("MPESA_PASSKEY") + timestamp
        password_bytes = password_str.encode("ascii")
        self.timestamp = timestamp
        return base64.b64encode(password_bytes).decode("utf-8")

    def refresh_token(self):
        if self.access_token_expiration and time.time() > self.access_token_expiration:
            self.access_token = self.get_access_token()
            self.access_token_expiration = time.time() + 3400
            self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def stk_push_request(self, db: Session, phone_number: str, amount: float, reference: str):
        #self.refresh_token()
        rand_number = str(random.randint(10000, 99999))
        req_data = {
            "BusinessShortCode": self.shortcode,
            "Password": self.password,
            "Timestamp": self.timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": math.ceil(float(amount)),
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.c2b_callback,
            "AccountReference": "AISTRAK PREDICTION",
            "TransactionDesc": reference,
            "BillRefNumber": "AISTRAK PREDICTION"
        }

        res = requests.post(
            self.checkout_url, json=req_data, headers=self.headers, timeout=30
        )
        res_data = res.json()
        logger.info(f"Mpesa request data {req_data}")
        logger.info(f"Mpesa response info {res_data}")

        if res.ok and "CheckoutRequestID" in res_data:
            mpesa_tx = MpesaTransaction(
                transaction_no=str(uuid4()),
                phone_number=phone_number,
                checkout_request_id=res_data["CheckoutRequestID"],
                reference=reference,
                amount=amount,
                status="Pending",
                created=datetime.now(),
                billref=reference
            )
            db.add(mpesa_tx)
            db.commit()
            db.refresh(mpesa_tx)
            res_data['billref'] = reference
            return res_data
        else:
            raise HTTPException(status_code=400, detail="Mpesa STK push failed")

    def handle_callback(self, db: Session, data: dict):
        try:
            status = data["Body"]["stkCallback"]["ResultCode"]
            checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
            mpesa_tx = db.query(MpesaTransaction).filter_by(checkout_request_id=checkout_request_id).first()
            if not mpesa_tx:
                raise HTTPException(status_code=404, detail="Transaction not found")

            if status == 0:
                items = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
                for item in items:
                    if item["Name"] == "Amount":
                        mpesa_tx.amount = item["Value"]
                    elif item["Name"] == "MpesaReceiptNumber":
                        mpesa_tx.receipt_no = item["Value"]
                    elif item["Name"] == "PhoneNumber":
                        mpesa_tx.phone_number = str(item["Value"])
                mpesa_tx.status = "Complete"

                # update the transaction in the database
                internal_tx = db.query(Transaction).filter_by(tx_hash=mpesa_tx.reference).first()
                if internal_tx:
                    internal_tx.status = "Complete"
                    internal_tx.mpesa_receipt = mpesa_tx.receipt_no

                    if internal_tx.tx_type == "Stake":
                        # update the prediction and wallet
                        complete_prediction_payment(db, mpesa_tx.reference)

            else:
                mpesa_tx.status = "Pending"

            db.commit()
            return {"status": "ok", "code": 0}
        except Exception as e:
            logger.error(f"Callback handling error: {e}")
            raise HTTPException(status_code=500, detail="Callback handling error")