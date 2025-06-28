from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import datetime
from fastapi import status
from ..models import UserPreferences
from ..database import get_user_preferences_collection
from fastapi.security import OAuth2PasswordBearer
from fastapi import Body
from pydantic import BaseModel

from auth_service.models import users, predictions, watchlist_stock_data, ensure_ttl_index
from auth_service.schemas import UserOut, WatchlistItem, PredictionIn, PredictionOut
from auth_service.security import decode_token
from fastapi import BackgroundTasks
import logging

router = APIRouter(prefix="/user", tags=["user"])

# Use the built-in HTTPBearer to pull the token from the Authorization header
bearer_scheme = HTTPBearer(auto_error=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(404, "User not found")
    # Ensure fields exist
    update_fields = {}
    if "first_name" not in user:
        update_fields["first_name"] = ""
    if "last_name" not in user:
        update_fields["last_name"] = ""
    if "bio" not in user:
        update_fields["bio"] = ""
    if update_fields:
        await users.update_one({"email": email}, {"$set": update_fields})
        user.update(update_fields)
    return {
        "id": str(user.get("_id", "")),
        "email": user["email"],
        "username": user.get("username", ""),
        "first_name": user.get("first_name", ""),
        "last_name": user.get("last_name", ""),
        "bio": user.get("bio", "")
    }

@router.put("/profile", response_model=UserOut)
async def update_profile(
    payload: dict = None,
    email: str = Depends(get_current_email)
):
    if payload is None:
        raise HTTPException(400, "No data provided")
    update_fields = {}
    for field in ["username", "first_name", "last_name", "bio"]:
        if field in payload:
            update_fields[field] = payload[field]
    if not update_fields:
        raise HTTPException(400, "No valid fields to update")
    await users.update_one({"email": email}, {"$set": update_fields})
    user = await users.find_one({"email": email})
    return {
        "id": str(user.get("_id", "")),
        "email": user["email"],
        "username": user.get("username", ""),
        "first_name": user.get("first_name", ""),
        "last_name": user.get("last_name", ""),
        "bio": user.get("bio", "")
    }

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
    return rec["watchlist"]

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
    return rec["watchlist"]

@router.get("/watchlist/data")
async def get_watchlist_data(email: str = Depends(get_current_email)):
    rec = await users.find_one({"email": email})
    print(f"DEBUG: Looking up user with email={email}, found={rec is not None}")
    if not rec or "watchlist" not in rec:
        print("DEBUG: No user or no watchlist field found.")
        return []
    symbols = rec["watchlist"]
    print(f"DEBUG: User's watchlist: {symbols}")
    data = []
    for symbol in symbols:
        doc = await watchlist_stock_data.find_one({"user_email": email, "ticker": symbol})
        print(f"DEBUG: Querying for user_email={email}, ticker={symbol} -> found={doc is not None}")
        if doc:
            entry = {}
            if "prediction" in doc:
                entry["prediction"] = doc["prediction"]
            if "fetchedStockData" in doc:
                entry["fetchedStockData"] = doc["fetchedStockData"]
            entry["ticker"] = symbol
            data.append(entry)
    print(f"DEBUG: Returning {len(data)} entries from watchlist_stock_data.")
    return data

@router.get("/watchlist/{ticker}")
async def get_watchlist_ticker(
    ticker: str,
    email: str = Depends(get_current_email)
):
    doc = await watchlist_stock_data.find_one({"user_email": email, "ticker": ticker})
    if not doc:
        raise HTTPException(404, "Stock not found in watchlist")
    # Return the entire document (excluding _id)
    doc.pop("_id", None)
    return doc

async def save_watchlist_stock_data(user_email, symbol, data):
    symbol_upper = symbol.upper()
    logger.info(f"Saving watchlist stock data for user_email={user_email}, symbol={symbol_upper}")
    # Remove duplicates before upserting
    duplicates = await watchlist_stock_data.count_documents({"user_email": user_email, "ticker": symbol_upper})
    if duplicates > 1:
        logger.warning(f"Found {duplicates} duplicate entries for user_email={user_email}, ticker={symbol_upper}. Removing all but one.")
        # Remove all duplicates
        await watchlist_stock_data.delete_many({"user_email": user_email, "ticker": symbol_upper})
    # Upsert the new/updated prediction
    await watchlist_stock_data.update_one(
        {"user_email": user_email, "ticker": symbol_upper},
        {"$set": {"data": data, "created_at": datetime.utcnow()}},
        upsert=True
    )

class FetchIn(BaseModel):
    ticker: str
    symbol: str
    technical_indicators: dict
    volume_features: dict
    fundamentals: dict
    news_sentiment: dict
    advanced_news_sentiment: dict
    extended_fundamentals: dict
    technical_indicators_ext: dict
    volume_features_ext: dict
    reasoning: dict
    timestamp: str = None

class FetchOut(BaseModel):
    ticker: str
    symbol: str
    technical_indicators: dict
    volume_features: dict
    fundamentals: dict
    news_sentiment: dict
    advanced_news_sentiment: dict
    extended_fundamentals: dict
    technical_indicators_ext: dict
    volume_features_ext: dict
    reasoning: dict
    prediction: dict = None
    timestamp: str = None

@router.post("/fetch", response_model=FetchOut)
async def save_fetch_data(
    payload: FetchIn,
    email: str = Depends(get_current_email)
):
    doc = payload.dict()
    doc["user_email"] = email
    doc["timestamp"] = doc.get("timestamp") or datetime.utcnow().isoformat()
    # Save under 'fetchedStockData'
    await watchlist_stock_data.update_one(
        {"user_email": email, "ticker": payload.ticker},
        {"$set": {"fetchedStockData": doc, "timestamp": doc["timestamp"]}},
        upsert=True
    )
    saved = await watchlist_stock_data.find_one({"user_email": email, "ticker": payload.ticker})
    if saved and "fetchedStockData" in saved:
        return saved["fetchedStockData"]
    else:
        return {}

@router.post("/prediction", response_model=PredictionOut)
async def save_prediction(
    payload: PredictionIn,
    email: str = Depends(get_current_email),
    background_tasks: BackgroundTasks = None
):
    # Save the LLM output and always include the latest fetchedStockData
    timestamp = datetime.utcnow().isoformat()
    # Fetch the latest fetchedStockData from the DB
    doc = await watchlist_stock_data.find_one({"user_email": email, "ticker": payload.ticker})
    update_fields = {"prediction": payload.prediction, "timestamp": timestamp}
    if doc and "fetchedStockData" in doc:
        update_fields["fetchedStockData"] = doc["fetchedStockData"]
    elif payload.fetchedStockData is not None:
        update_fields["fetchedStockData"] = payload.fetchedStockData
    await watchlist_stock_data.update_one(
        {"user_email": email, "ticker": payload.ticker},
        {"$set": update_fields},
        upsert=True
    )
    return {"ticker": payload.ticker, "prediction": payload.prediction, "timestamp": timestamp}

@router.get("/prediction/{ticker}", response_model=PredictionOut)
async def get_prediction(
    ticker: str,
    email: str = Depends(get_current_email)
):
    doc = await predictions.find_one({"email": email, "ticker": ticker})
    if not doc:
        raise HTTPException(404, "Prediction not found")
    return {
        "ticker": doc["ticker"],
        "prediction": doc["prediction"],
        "timestamp": doc["timestamp"]
    }

@router.get("/predictions", response_model=List[PredictionOut])
async def get_all_predictions(email: str = Depends(get_current_email)):
    # Try to get predictions from user document first
    rec = await users.find_one({"email": email})
    if rec and "predictions" in rec:
        return rec["predictions"]
    # Fallback to predictions collection
    cursor = predictions.find({"email": email})
    results = []
    async for doc in cursor:
        results.append({
            "ticker": doc["ticker"],
            "prediction": doc["prediction"],
            "timestamp": doc["timestamp"]
        })
    return results

# Dummy dependency for user_id extraction (replace with real auth)
def get_current_user_id():
    # Replace with actual logic to extract user_id from JWT/session
    return "dummy_user_id"

@router.get("/api/user/preferences", response_model=UserPreferences)
def get_preferences(user_id: str = Depends(get_current_user_id)):
    collection = get_user_preferences_collection()
    prefs = collection.find_one({"userId": user_id})
    if not prefs:
        # Return default preferences if not set
        prefs = UserPreferences(userId=user_id)
        collection.insert_one(prefs.dict())
    return UserPreferences(**prefs)

@router.put("/api/user/preferences", response_model=UserPreferences)
def update_preferences(preferences: UserPreferences, user_id: str = Depends(get_current_user_id)):
    collection = get_user_preferences_collection()
    result = collection.update_one({"userId": user_id}, {"$set": preferences.dict()}, upsert=True)
    if result.matched_count == 0 and result.upserted_id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update preferences.")
    return preferences

# New: Model for technical data only (no reasoning required)
class TechnicalDataIn(BaseModel):
    ticker: str
    symbol: str
    technical_indicators: dict
    volume_features: dict
    fundamentals: dict
    news_sentiment: dict
    advanced_news_sentiment: dict
    extended_fundamentals: dict
    technical_indicators_ext: dict
    volume_features_ext: dict
    timestamp: str = None

# New: Save technical data endpoint
@router.post("/technical-data")
async def save_technical_data(
    payload: TechnicalDataIn,
    email: str = Depends(get_current_email)
):
    doc = payload.dict()
    doc["user_email"] = email
    doc["timestamp"] = doc.get("timestamp") or datetime.utcnow().isoformat()
    # Save under 'fetchedStockData' (like /fetch, but no reasoning required)
    await watchlist_stock_data.update_one(
        {"user_email": email, "ticker": payload.ticker},
        {"$set": {"fetchedStockData": doc, "timestamp": doc["timestamp"]}},
        upsert=True
    )
    saved = await watchlist_stock_data.find_one({"user_email": email, "ticker": payload.ticker})
    if saved and "fetchedStockData" in saved:
        return saved["fetchedStockData"]
    else:
        return {}
