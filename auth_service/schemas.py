from pydantic import BaseModel, EmailStr
from typing import List

class UserIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class WatchlistItem(BaseModel):
    symbol: str

class WatchlistOut(BaseModel):
    watchlist: List[str]

