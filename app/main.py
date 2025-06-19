#app/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from app.model_service import predict_next_10_days
import redis, os
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

redis_client = redis.from_url(os.getenv("REDIS_URL"))

app = FastAPI()

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

# Input schema
class PredictionRequest(BaseModel):
    stock_symbol: str

# Output schema
class PredictionResponse(BaseModel):
    predictions: list[dict]

# Route
@app.post("/predict", response_model=PredictionResponse)
async def predict_endpoint(data: PredictionRequest):
    preds = predict_next_10_days(data.stock_symbol)
    last_date = datetime.today()
    formatted_preds = [
        {
            "date": d.strftime("%d/%m/%Y"),
            "predicted_price": round(float(p), 2)
        }
        for d, p in zip(
            pd.bdate_range(last_date + timedelta(days=1), periods=len(preds)),
            preds
        )
    ]
    return {"predictions": formatted_preds}
