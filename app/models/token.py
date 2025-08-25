from sqlalchemy import Column, String, Boolean, DateTime, Float, Enum, ForeignKey, Integer, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON as MySQLJSON
from uuid import uuid4
from datetime import datetime
from app.core.database import Base
import enum

class Token(Base):
    __tablename__ = "tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    symbol = Column(String(20), unique=True)
    name = Column(String(100))
    is_active = Column(Boolean)
    logo_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)

class TokenProposal(Base):
    __tablename__ = "token_proposals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    proposed_by = Column(String(36), ForeignKey("users.id"))
    token_symbol = Column(String(10), nullable=False)
    token_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum("active", "approved", "rejected", "expired", name="proposal_status"), default="active")
    total_votes = Column(Integer, default=0)
    votes_needed = Column(Integer, default=1000)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

class ProposalVote(Base):
    __tablename__ = "proposal_votes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    proposal_id = Column(String(36), ForeignKey("token_proposals.id"))
    user_id = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)