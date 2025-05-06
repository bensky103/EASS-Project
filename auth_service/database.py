from motor.motor_asyncio import AsyncIOMotorClient
import os

client = AsyncIOMotorClient(
    os.getenv("MONGO_URI", "mongodb://mongo:27017")
)
db = client.get_default_database()

