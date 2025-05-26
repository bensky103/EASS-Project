# stock_data_fetching/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from fetch_price_data import fetch_price_data
from calculate_indicators import add_technical_indicators
from calculate_volume_features import calculate_volume_features
from fetch_fundamentals import fetch_fundamentals
from send_to_chatgpt import send_features_to_gpt
from config import settings
from logger import logger

app = FastAPI(
    title="Stock Data Fetching Service",
    description="Service for fetching and analyzing stock data using Alpha Vantage and OpenAI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StockAnalysisRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = settings.DEFAULT_TIMEFRAME

class StockAnalysisResponse(BaseModel):
    symbol: str
    analysis: Dict[str, Any]
    technical_indicators: Dict[str, float]
    volume_features: Dict[str, float]
    fundamentals: Dict[str, Any]
    gpt_analysis: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.SERVICE_NAME}

@app.post("/analyze", response_model=StockAnalysisResponse)
async def analyze_stock(request: StockAnalysisRequest):
    """
    Analyze a stock using technical indicators, volume features, and GPT analysis
    """
    try:
        logger.info(f"Starting analysis for symbol: {request.symbol}")
        
        # Fetch price data
        df = fetch_price_data(request.symbol, settings.ALPHA_VANTAGE_API_KEY)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {request.symbol}")
        
        # Calculate indicators and features
        df = add_technical_indicators(df)
        volume_features = calculate_volume_features(df)
        fundamentals = fetch_fundamentals(request.symbol, settings.ALPHA_VANTAGE_API_KEY)
        
        # Prepare technical indicators
        technical_indicators = {
            "latest_close": float(df["close"].iloc[-1]),
            "sma_5": float(df["sma_5"].iloc[-1]),
            "ema_5": float(df["ema_5"].iloc[-1]),
            "macd": float(df["macd"].iloc[-1]),
            "bb_upper": float(df["bb_upper"].iloc[-1]),
            "bb_lower": float(df["bb_lower"].iloc[-1])
        }
        
        # Prepare final payload for GPT
        final_payload = {
            "symbol": request.symbol,
            **technical_indicators,
            **volume_features,
            **fundamentals
        }
        
        # Get GPT analysis
        gpt_response = send_features_to_gpt(final_payload, settings.OPENAI_API_KEY)
        
        logger.info(f"Successfully completed analysis for {request.symbol}")
        
        return StockAnalysisResponse(
            symbol=request.symbol,
            analysis=final_payload,
            technical_indicators=technical_indicators,
            volume_features=volume_features,
            fundamentals=fundamentals,
            gpt_analysis=gpt_response
        )
        
    except Exception as e:
        logger.error(f"Error analyzing stock {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

