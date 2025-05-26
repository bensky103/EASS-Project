from fastapi import APIRouter, HTTPException, status, Body
from auth_service.schemas import UserIn, Token
from auth_service.models import users
from auth_service.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=201)
async def register(payload: dict = Body(...)):                  
    u = UserIn(**payload)
    if await users.find_one({"email": u.email}):
        raise HTTPException(400, "Email already registered")
    pw_hash = hash_password(u.password)
    await users.insert_one({"email": u.email, "passwordHash": pw_hash, "watchlist": []})
    return {"email": u.email}

@router.post("/login", response_model=Token)
async def login(payload: dict = Body(...)):                      
    u = UserIn(**payload)
    rec = await users.find_one({"email": u.email})
    if not rec or not verify_password(u.password, rec["passwordHash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = create_access_token({"sub": u.email})
    return {"access_token": token}

