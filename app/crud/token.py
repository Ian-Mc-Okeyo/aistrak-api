from sqlalchemy.orm import Session
from app.schemas.token import CreateToken, CreateTokenProposal, CreateProposalVote
from app.models.token import Token, TokenProposal, ProposalVote
from app.models.user import User
from datetime import datetime, timedelta
from app.models.transaction import Transaction
from fastapi import HTTPException
from app.crud.mpesa import MpesaGateWay
import random
import string

mpesa_gateway = MpesaGateWay()

def random_10_letter_string():
    return ''.join(random.choices(string.ascii_letters, k=10))

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

# create token proposal
def create_mpesa_token_proposal(db: Session, proposal: CreateTokenProposal, user_id: str):
    # check if the user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_proposal = TokenProposal(
        proposed_by=user_id,
        token_symbol=proposal.token_symbol,
        token_name=proposal.token_name,
        description=proposal.description,
        votes_needed=3, # for testing
        payment_reference=random_10_letter_string(),
        expires_at=datetime.now() + timedelta(days=28) # proposals expire in 28 days
    )

    # create the internal transaction
    internal_tx = Transaction(
        user_id=user_id,
        amount=proposal.amount,
        tx_type="Proposal",
        status="Pending",
        payment_method=proposal.payment_method,
        tx_hash=db_proposal.payment_reference
    )

    db.add(internal_tx)
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)

    if proposal.payment_method == "mpesa" and proposal.phone_number:

        mpesa_gateway.stk_push_request(
            db=db,
            phone_number=proposal.phone_number,
            amount=proposal.amount,
            reference=db_proposal.payment_reference
        )

    return db_proposal

# create proposal vote
def create_proposal_vote(db: Session, vote: CreateProposalVote, user_id: str):
    # check if the proposal exists and is active
    proposal = db.query(TokenProposal).filter(TokenProposal.id == vote.proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.status != "active":
        raise HTTPException(status_code=400, detail="Proposal is not active")
    if proposal.payment_status != "Complete":
        raise HTTPException(status_code=400, detail="Proposal payment is not complete")
    if proposal.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Proposal has expired")

    # check if the user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # check if the user has already voted for this proposal
    existing_vote = db.query(ProposalVote).filter(
        ProposalVote.proposal_id == vote.proposal_id,
        ProposalVote.user_id == user_id,
        ProposalVote.payment_status == "Complete"
    ).first()

    if existing_vote:
        raise HTTPException(status_code=400, detail="User has already voted for this proposal")

    db_vote = ProposalVote(
        proposal_id=vote.proposal_id,
        user_id=user_id,
        payment_reference=random_10_letter_string()
    )

    # create the internal transaction
    internal_tx = Transaction(
        user_id=user_id,
        amount=1.0,  # voting fee
        tx_type="Vote",
        status="Pending",
        payment_method=vote.payment_method,
        tx_hash=db_vote.payment_reference
    )

    db.add(internal_tx)
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)

    if vote.payment_method == "mpesa" and vote.phone_number:

        mpesa_gateway.stk_push_request(
            db=db,
            phone_number=vote.phone_number,
            amount=1.0,
            reference=db_vote.payment_reference
        )
    
    return db_vote

# get token proposals
def get_token_proposals(db: Session):
    results = (
        db.query(
            TokenProposal,
            User.username.label("proposer_username")
        )
        .join(User, TokenProposal.proposed_by == User.id)
        .filter(TokenProposal.payment_status == "Complete")
        .all()
    )
    # Combine results into dicts
    return [
        {
            "id": proposal.id,
            "token_symbol": proposal.token_symbol,
            "token_name": proposal.token_name,
            "description": proposal.description,
            "status": proposal.status,
            "proposed_by": proposer_username,
            "total_votes": proposal.total_votes,
            "votes_needed": proposal.votes_needed,
            "expires_at": proposal.expires_at,
            "created_at": proposal.created_at,
        }
        for proposal, proposer_username in results
    ]

# count user total votes
def count_user_votes(db: Session, user_id: str):
    return db.query(ProposalVote).filter(
        ProposalVote.user_id == user_id,
        ProposalVote.payment_status == "Complete"
    ).count()