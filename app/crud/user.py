from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User, UserSetting
from app.models.wallet import UserWallet
from fastapi import HTTPException
from sqlalchemy.orm import Session

def create_user(db, user: UserCreate):
    # ensure the user Id does not exist
    print("Trying to create the user")
    # print(user)
    user_exists = db.query(User).filter(User.id == user["id"]).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="User with this ID already exists")
    
    # check if the email already exists
    email_exists = db.query(User).filter(User.email == user["email"]).first()
    if email_exists:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # either email or web3 wallet address should be provided
    if not user.get("email") and not user.get("wallet_address"):
        raise HTTPException(status_code=400, detail="Either email or wallet address must be provided")

    # set the auth type
    if user.get("email"):
        user["auth_type"] = "email"
    elif user.get("wallet_address"):
        user["auth_type"] = "wallet"

    user = User(**user)
    user_wallet = UserWallet(user_id=user.id)
    user_setting = UserSetting(user_id=user.id)
    
    db.add(user)
    db.add(user_wallet)
    db.add(user_setting)

    db.commit()
    db.refresh(user)
    return user

def update_clerk_user(db, user: UserUpdate, id: str):
    # ensure the user Id exists
    print("Trying to update the user")
    print(user)
    user_exists = db.query(User).filter(User.id == id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User with this ID does not exist")
    
    # update the user
    for key, value in user.items():
        setattr(user_exists, key, value)
    
    db.commit()
    db.refresh(user_exists)
    return user_exists

def get_user_wallet(db: Session, user_id: str):
    user_wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
    return user_wallet