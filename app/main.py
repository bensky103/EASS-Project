#app/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from app.model_service import predict
import redis, os

redis_client = redis.from_url(os.getenv("REDIS_URL"))

app = FastAPI()

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

# Input schema
class PredictionRequest(BaseModel):
    stock_symbol: str
    historical_data: list[float]

# Output schema
class PredictionResponse(BaseModel):
    predicted_price: float
    confidence: float

# Route
@app.post("/predict", response_model=PredictionResponse)
async def predict_endpoint(data: PredictionRequest):
    return predict(data.stock_symbol, data.historical_data)
