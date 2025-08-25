from sqlalchemy.orm import Session
from app.schemas.token import CreateToken
from app.models.token import Token

# create token
def create_token(db: Session, token: CreateToken):
    db_token = Token(**token.dict())
    db_token.is_active = True
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_all_tokens(db: Session):
    return db.query(Token).all()