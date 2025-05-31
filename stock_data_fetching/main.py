# stock_data_fetching/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, Union
import uvicorn
import pandas as pd

from stock_data_fetching.fetch_price_data import fetch_price_data
from stock_data_fetching.calculate_indicators import add_technical_indicators
from stock_data_fetching.calculate_volume_features import calculate_volume_features
from stock_data_fetching.fetch_fundamentals import fetch_fundamentals
from stock_data_fetching.config import settings
from stock_data_fetching.logger import logger

app = FastAPI(
    title="Stock Data Fetching Service",
    description="Service for fetching and analyzing stock data using Alpha Vantage",
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

class StockDataRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = settings.DEFAULT_TIMEFRAME

class StockDataResponse(BaseModel):
    symbol: str
    technical_indicators: Dict[str, float]
    volume_features: Dict[str, Union[float, str]]
    fundamentals: Dict[str, Any]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.SERVICE_NAME}

@app.post("/fetch", response_model=StockDataResponse)
async def fetch_stock_data(request: StockDataRequest):
    """
    Fetch stock data including technical indicators, volume features, and fundamentals
    """
    try:
        logger.info(f"Starting data fetch for symbol: {request.symbol}")
        
        # Fetch price data
        df = fetch_price_data(request.symbol, settings.ALPHA_VANTAGE_API_KEY)
        logger.info(f"Raw price data shape: {df.shape}")
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {request.symbol}")
        
        logger.info("Price data fetched successfully")
        
        # Calculate indicators and features
        try:
            df = add_technical_indicators(df)
            logger.info(f"Technical indicators added. New columns: {df.columns.tolist()}")
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
                "sma_5": float(df["sma_5"].iloc[-1]) if pd.notna(df["sma_5"].iloc[-1]) else 0.0,
                "ema_5": float(df["ema_5"].iloc[-1]) if pd.notna(df["ema_5"].iloc[-1]) else 0.0,
                "macd": float(df["macd"].iloc[-1]) if pd.notna(df["macd"].iloc[-1]) else 0.0,
                "macd_signal": float(df["macd_signal"].iloc[-1]) if pd.notna(df["macd_signal"].iloc[-1]) else 0.0,
                "macd_hist": float(df["macd_hist"].iloc[-1]) if pd.notna(df["macd_hist"].iloc[-1]) else 0.0,
                "bb_upper": float(df["bb_upper"].iloc[-1]) if pd.notna(df["bb_upper"].iloc[-1]) else 0.0,
                "bb_middle": float(df["bb_middle"].iloc[-1]) if pd.notna(df["bb_middle"].iloc[-1]) else 0.0,
                "bb_lower": float(df["bb_lower"].iloc[-1]) if pd.notna(df["bb_lower"].iloc[-1]) else 0.0
            }
            logger.info(f"Technical indicators prepared: {technical_indicators}")
        except Exception as e:
            logger.error(f"Error preparing technical indicators: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error preparing technical indicators: {str(e)}")
        
        logger.info(f"Successfully completed data fetch for {request.symbol}")
        
        response = StockDataResponse(
            symbol=request.symbol,
            technical_indicators=technical_indicators,
            volume_features=volume_features,
            fundamentals=fundamentals
        )
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching stock data for {request.symbol}: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

