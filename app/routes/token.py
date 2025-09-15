from fastapi import APIRouter, Request, HTTPException, Depends
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.crud.token import create_token, get_all_tokens, create_mpesa_token_proposal, get_token_proposals, create_proposal_vote, count_user_votes
from app.schemas.token import CreateToken, CreateTokenProposal, CreateProposalVote
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

# create token proposal
@router.post("/propose")
def create_token_proposal_router(request: Request, proposal: CreateTokenProposal, db: Session = Depends(get_db)):
    user = authenticate_and_get_user_details(request)

    db_proposal = create_mpesa_token_proposal(db=db, proposal=proposal, user_id=user['user_id'])

    if not db_proposal:
        raise HTTPException(status_code=400, detail="Token proposal creation failed")
    return {"status": "success", "proposal": db_proposal, "reference": db_proposal.payment_reference}

# get token proposals
@router.get("/proposals")
def get_token_proposals_router(request: Request, db: Session = Depends(get_db)):
    authenticate_and_get_user_details(request)

    proposals = get_token_proposals(db=db)
    return {"status": "success", "proposals": proposals}

# vote for a proposal
@router.post("/vote")
def vote_for_proposal_router(request: Request, vote: CreateProposalVote, db: Session = Depends(get_db)):
    user = authenticate_and_get_user_details(request)

    db_vote = create_proposal_vote(db=db, vote=vote, user_id=user['user_id'])

    if not db_vote:
        raise HTTPException(status_code=400, detail="Voting failed")
    return {"status": "success", "vote": db_vote, "reference": db_vote.payment_reference}

# count user votes
@router.get("/votes/count")
def count_user_votes_router(request: Request, db: Session = Depends(get_db)):
    user = authenticate_and_get_user_details(request)

    total_votes = count_user_votes(db=db, user_id=user['user_id'])

    return {"status": "success", "total_votes": total_votes}

