from .database import db
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

users = db.users      # collection for users
profiles = db.profiles  # optional user profiles
predictions = db.predictions  # collection for user predictions
watchlist_stock_data = db.watchlist_stock_data

# Ensure TTL index is created (run once at startup)
async def ensure_ttl_index():
    await watchlist_stock_data.create_index("created_at", expireAfterSeconds=604800)

class User(BaseModel):
    id: str = Field(default_factory=str, alias="_id")
    username: str
    email: EmailStr
    password: str
    firstName: str = ""
    lastName: str = ""
    profilePicture: str = ""
    bio: str = ""
    joinedDate: datetime = Field(default_factory=datetime.utcnow)
    emailVerified: bool = False
    accountType: str = "basic"

class UserPreferences(BaseModel):
    userId: str
    darkMode: bool = False
    emailNotifications: bool = True
    pushNotifications: bool = False

