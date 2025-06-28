from pydantic import BaseModel
from typing import List

class UserIn(BaseModel):
    email: str
    password: str
    username: str
    first_name: str = ""
    last_name: str = ""
    bio: str = ""

class UserOut(BaseModel):
    id: str
    email: str
    username: str
    first_name: str = ""
    last_name: str = ""
    bio: str = ""

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class WatchlistItem(BaseModel):
    symbol: str

class WatchlistOut(BaseModel):
    watchlist: List[str]

class PredictionIn(BaseModel):
    ticker: str
    prediction: dict
    fetchedStockData: dict = None

class PredictionOut(BaseModel):
    ticker: str
    prediction: dict
    timestamp: str

