from fastapi import APIRouter, Depends, HTTPException
from typing import List
from auth_service.models import users
from auth_service.schemas import UserOut, WatchlistItem, WatchlistOut
from auth_service.security import decode_token

router = APIRouter(prefix="/user", tags=["user"])

def get_current_email(token: str = Depends(lambda: None)):
    # In real code use OAuth2PasswordBearer + Depends; simplified here:
    from fastapi import Security, HTTPException
    from fastapi.security import HTTPBearer
    bearer = HTTPBearer(auto_error=True)
    creds = bearer(token)
    try:
        payload = decode_token(creds.credentials)
        return payload["sub"]
    except:
        raise HTTPException(401, "Invalid or expired token")

@router.get("/profile", response_model=UserOut)
async def profile(email: str = Depends(get_current_email)):
    return {"email": email}

@router.get("/watchlist", response_model=WatchlistOut)
async def get_watchlist(email: str = Depends(get_current_email)):
    rec = await users.find_one({"email": email})
    return {"watchlist": rec.get("watchlist", [])}

@router.post("/watchlist", response_model=WatchlistOut)
async def add_watchlist(item: WatchlistItem, email: str = Depends(get_current_email)):
    await users.update_one({"email": email}, {"$addToSet": {"watchlist": item.symbol}})
    rec = await users.find_one({"email": email})
    return {"watchlist": rec["watchlist"]}

@router.delete("/watchlist/{symbol}", response_model=WatchlistOut)
async def remove_watchlist(symbol: str, email: str = Depends(get_current_email)):
    await users.update_one({"email": email}, {"$pull": {"watchlist": symbol}})
    rec = await users.find_one({"email": email})
    return {"watchlist": rec["watchlist"]}

