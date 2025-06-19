from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from auth_service.models import users
from auth_service.schemas import UserOut, WatchlistItem
from auth_service.security import decode_token

router = APIRouter(prefix="/user", tags=["user"])

# Use the built-in HTTPBearer to pull the token from the Authorization header
bearer_scheme = HTTPBearer(auto_error=True)

def get_current_email(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    token = credentials.credentials
    try:
        payload = decode_token(token)
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.get("/profile", response_model=UserOut)
async def profile(email: str = Depends(get_current_email)):
    return {"email": email}

@router.get("/watchlist", response_model=List[str])
async def get_watchlist(email: str = Depends(get_current_email)):
    rec = await users.find_one({"email": email})
    if not rec:
        return []                          
    return rec.get("watchlist", [])

@router.post("/watchlist", response_model=List[str])
async def add_watchlist(
    item: WatchlistItem,
    email: str = Depends(get_current_email)
):
    await users.update_one(
        {"email": email},
        {"$addToSet": {"watchlist": item.symbol}}
    )
    rec = await users.find_one({"email": email})
    return {"watchlist": rec["watchlist"]}

@router.delete("/watchlist/{symbol}", response_model=List[str])
async def remove_watchlist(
    symbol: str,
    email: str = Depends(get_current_email)
):
    await users.update_one(
        {"email": email},
        {"$pull": {"watchlist": symbol}}
    )
    rec = await users.find_one({"email": email})
    return {"watchlist": rec["watchlist"]}
