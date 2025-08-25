from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateToken(BaseModel):
    symbol: str
    name: str
    logo_url: str