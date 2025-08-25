from fastapi import APIRouter, Request, HTTPException, Depends
import os
import json
from svix.webhooks import Webhook
from app.core.database import get_db
from app.crud.user import create_user, update_clerk_user
from dotenv import load_dotenv
from app.schemas.user import UserCreate

load_dotenv()

router = APIRouter()

@router.post("/user/create")
async def handle_user_created(request: Request, db = Depends(get_db)):
    webhook_secret = os.getenv("CLERK_USER_CREATE_WEBHOOK_SECRET")

    if not webhook_secret:
        print("CLERK_USER_CREATE_WEBHOOK_SECRET not set")
        raise HTTPException(status_code=500, detail="CLERK_USER_CREATE_WEBHOOK_SECRET not set")

    body = await request.body()
    payload = body.decode("utf-8")
    headers = dict(request.headers)

    wh = Webhook(webhook_secret)
    wh.verify(payload, headers)
    data = json.loads(payload)
    if data.get("type") != "user.created":
        print("Webhook type is not user.created")
        return {"status": "ignored"}
    user_data = data.get("data", {})
    print("user data", user_data)

    # get the email:
    emails = user_data.get("email_addresses")
    wallets = user_data.get("web3_wallets")
    user_data = {
        "id": user_data.get("id"),
        "email": emails[0].get("email_address") if emails else None,
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "avatar_url": user_data.get("profile_image_url"),
        "username": user_data.get("username"),
        "wallet_address": wallets[0].get("web3_wallet") if wallets else None,
    }

    #print("email", user_data.get("email"))
    create_user(db, user_data)
    return {"status": "success"}

@router.post("/user/update")
async def handle_user_update(request: Request, db = Depends(get_db)):
    webhook_secret = os.getenv("CLERK_USER_UPDATE_WEBHOOK_SECRET")

    if not webhook_secret:
        print("CLERK_USER_CREATE_WEBHOOK_SECRET not set")
        raise HTTPException(status_code=500, detail="CLERK_USER_CREATE_WEBHOOK_SECRET not set")

    body = await request.body()
    payload = body.decode("utf-8")
    headers = dict(request.headers)

    wh = Webhook(webhook_secret)
    wh.verify(payload, headers)
    data = json.loads(payload)
    if data.get("type") != "user.updated":
        print("Webhook type is not user.updated")
        return {"status": "ignored"}
    user_data = data.get("data", {})
    id= user_data.get("id")
    #print("user data", user_data)
    user_data = {
        "email": user_data.get("email_addresses", [{}])[0].get("email_address"),
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "avatar_url": user_data.get("profile_image_url"),
        "username": user_data.get("username"),
        "wallet_address": user_data.get("web3_wallets", [{}])[0].get("web3_wallet"),
    }
    update_clerk_user(db, user_data, id)
    return {"status": "success"}

    