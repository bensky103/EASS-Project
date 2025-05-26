from motor.motor_asyncio import AsyncIOMotorClient
import os

# Pull your URI from ENV (or default to the Mongo service)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")   
# Pick a database name—tests will use “test” by default
MONGO_DB  = os.getenv("MONGO_DB", "test")                      

# Connect and select
client = AsyncIOMotorClient(MONGO_URI)
db     = client[MONGO_DB]                                   
