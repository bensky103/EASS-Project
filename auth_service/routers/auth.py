from fastapi import APIRouter, HTTPException, status, Body, Depends
from auth_service.schemas import UserIn, Token
from auth_service.models import users
from auth_service.security import hash_password, verify_password, create_access_token, decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["auth"])

bearer_scheme = HTTPBearer(auto_error=True)

def get_current_email(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = decode_token(token)
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/register", status_code=201)
async def register(payload: dict = Body(...)):                  
    u = UserIn(**payload)
    if await users.find_one({"email": u.email}):
        raise HTTPException(400, "Email already registered")
    pw_hash = hash_password(u.password)
    result = await users.insert_one({
        "email": u.email,
        "passwordHash": pw_hash,
        "username": u.username,
        "watchlist": []
    })
    user_id = str(result.inserted_id)
    return {"id": user_id, "email": u.email, "username": u.username}

@router.post("/login", response_model=Token)
async def login(payload: dict = Body(...)):                      
    email = payload.get("email")
    password = payload.get("password")
    rec = await users.find_one({"email": email})
    if not rec or not verify_password(password, rec["passwordHash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = create_access_token({"sub": email})
    return {"access_token": token}

@router.get("/me")
async def get_me(email: str = Depends(get_current_email)):
    user = await users.find_one({"email": email})
    if not user:
        raise HTTPException(404, "User not found")
    return {"id": str(user["_id"]), "email": user["email"], "username": user.get("username", "")}

