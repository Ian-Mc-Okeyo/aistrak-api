from fastapi import APIRouter, Request, HTTPException, Depends
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.crud.token import create_token, get_all_tokens
from app.schemas.token import CreateToken
from app.models.token import Token
from app.util import authenticate_and_get_user_details

router = APIRouter()

@router.post("/create")
def create_new_token_router(request: Request, token: CreateToken, db: Session = Depends(get_db)):
    db_token = create_token(db=db, token=token)
    if not db_token:
        raise HTTPException(status_code=400, detail="Token creation failed")
    return {"status": "success", "token": db_token}

# get all tokens
@router.get("/all")
async def get_all_tokens_router(request: Request, db: Session = Depends(get_db)):
    tokens = get_all_tokens(db=db)
    return {"status": "success", "tokens": tokens}
