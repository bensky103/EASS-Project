from pydantic import BaseModel
from typing import List

class UserIn(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class WatchlistItem(BaseModel):
    symbol: str

class WatchlistOut(BaseModel):
    watchlist: List[str]

