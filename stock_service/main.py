#stock_service/main.py

from fastapi import FastAPI
from stock_service.routes.stock import router as stock_router
from fastapi.middleware.cors import CORSMiddleware
import redis, os

redis_client = redis.from_url(os.getenv("REDIS_URL"))

app = FastAPI(title="Stock-Data Service")

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
  
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(stock_router)

