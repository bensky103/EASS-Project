# stock_data_fetching/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import pandas as pd

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
        logger.info(f"Raw price data shape: {df.shape}")
        logger.info(f"Price data columns: {df.columns.tolist()}")
        logger.info(f"First few rows of price data:\n{df.head().to_string()}")
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {request.symbol}")
        
        logger.info("Price data fetched successfully")
        
        # Calculate indicators and features
        try:
            df = add_technical_indicators(df)
            logger.info(f"Technical indicators added. New columns: {df.columns.tolist()}")
            logger.info(f"Technical indicators sample:\n{df.tail().to_string()}")
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error calculating technical indicators: {str(e)}")
            
        try:
            volume_features = calculate_volume_features(df)
            logger.info(f"Volume features calculated: {volume_features}")
        except Exception as e:
            logger.error(f"Error calculating volume features: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error calculating volume features: {str(e)}")
            
        try:
            fundamentals = fetch_fundamentals(request.symbol, settings.ALPHA_VANTAGE_API_KEY)
            logger.info(f"Fundamentals fetched: {fundamentals}")
        except Exception as e:
            logger.error(f"Error fetching fundamentals: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching fundamentals: {str(e)}")
        
        # Prepare technical indicators with error checking
        try:
            technical_indicators = {
                "latest_close": float(df["close"].iloc[-1]),
                "sma_5": float(df["sma_5"].iloc[-1]) if pd.notna(df["sma_5"].iloc[-1]) else None,
                "ema_5": float(df["ema_5"].iloc[-1]) if pd.notna(df["ema_5"].iloc[-1]) else None,
                "macd": float(df["macd"].iloc[-1]) if pd.notna(df["macd"].iloc[-1]) else None,
                "bb_upper": float(df["bb_upper"].iloc[-1]) if pd.notna(df["bb_upper"].iloc[-1]) else None,
                "bb_lower": float(df["bb_lower"].iloc[-1]) if pd.notna(df["bb_lower"].iloc[-1]) else None
            }
            logger.info(f"Technical indicators prepared: {technical_indicators}")
        except Exception as e:
            logger.error(f"Error preparing technical indicators: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error preparing technical indicators: {str(e)}")
        
        # Prepare final payload for GPT
        final_payload = {
            "symbol": request.symbol,
            **technical_indicators,
            **volume_features,
            **fundamentals
        }
        logger.info(f"Final payload prepared: {final_payload}")
        
        # Get GPT analysis
        try:
            gpt_response = send_features_to_gpt(final_payload, settings.OPENAI_API_KEY)
            logger.info(f"GPT analysis received: {gpt_response[:200]}...")  # Log first 200 chars
        except Exception as e:
            logger.error(f"Error getting GPT analysis: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting GPT analysis: {str(e)}")
        
        logger.info(f"Successfully completed analysis for {request.symbol}")
        
        response = StockAnalysisResponse(
            symbol=request.symbol,
            analysis=final_payload,
            technical_indicators=technical_indicators,
            volume_features=volume_features,
            fundamentals=fundamentals,
            gpt_analysis=gpt_response
        )
        logger.info(f"Response prepared: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing stock {request.symbol}: {str(e)}")
        logger.exception("Full traceback:")  # This will log the full stack trace
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

