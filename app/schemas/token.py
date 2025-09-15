from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateToken(BaseModel):
    symbol: str
    name: str
    logo_url: str

class CreateTokenProposal(BaseModel):
    token_symbol: str
    token_name: str
    description: str
    phone_number: Optional[str] = None
    payment_method: Optional[str] = "internal" 
    amount: Optional[float] = 10.0  # Proposal fee

class CreateProposalVote(BaseModel):
    proposal_id: str
    payment_method: Optional[str] = "internal"
    amount: Optional[float] = 1.0  # Voting fee
    phone_number: Optional[str] = None