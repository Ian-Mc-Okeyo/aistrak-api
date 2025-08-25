from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    id: str
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    auth_type: Optional[str] = None
    wallet_address: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    title: Optional[str]
    description: Optional[str]
    avatar_url: Optional[str]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]