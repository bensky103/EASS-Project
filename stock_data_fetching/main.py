# stock_data_fetching/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Dict, Any, Optional, Union
import uvicorn
import pandas as pd
import requests
import hashlib
import json
import re

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

# LLM prompt helper

def format_llm_prompt(symbol: str, features: Dict[str, Any]) -> str:
    open_price = features.get('open', 'N/A')
    close_price = features.get('close', 'N/A')
    high_price = features.get('high', 'N/A')
    low_price = features.get('low', 'N/A')
    volume = features.get('volume', 'N/A')
    sma_10 = features.get('sma_10', 'N/A')
    rsi = features.get('rsi', 'N/A')
    macd = features.get('macd', 'N/A')

    fiscal_date_ending = features.get('fiscalDateEnding', 'N/A')
    reported_eps = features.get('reportedEPS', 'N/A')
    estimated_eps = features.get('estimatedEPS', 'N/A')
    surprise = features.get('surprise', 'N/A')
    surprise_percentage = features.get('surprisePercentage', 'N/A')

    prompt = f"""
You are a professional financial analyst AI model.

Your task is to evaluate a stock based on the following features, using technical analysis as the primary method and incorporating fundamental data as supporting context.

Use recent price action, momentum indicators, and earnings performance to determine whether the stock should be bought, sold, or held.

Stock Symbol: {symbol}

Stock Data:
[TECHNICAL INDICATORS]
Open Price: {open_price}
Close Price: {close_price}
Daily High: {high_price}
Daily Low: {low_price}
Volume: {volume}
10-Day Simple Moving Average (SMA): {sma_10}
Relative Strength Index (RSI): {rsi}
MACD Value: {macd}

[FUNDAMENTALS]
Fiscal Date Ending: {fiscal_date_ending}
Reported EPS: {reported_eps}
Estimated EPS: {estimated_eps}
Earnings Surprise: {surprise}
Surprise Percentage: {surprise_percentage}

Instructions:
Use technical indicators to analyze momentum, trend strength, overbought/oversold conditions, and trend reversal signals.
Use fundamental data to confirm or challenge technical conclusions, especially focusing on earnings surprise and EPS performance.

Take note of key relationships:
If RSI > 70 and MACD is bearish, it may indicate overbought conditions.
If Close crosses above SMA and MACD turns positive, this may indicate a bullish signal.
Positive earnings surprise may reinforce a BUY recommendation.

Question:
Should I BUY, SELL, or HOLD this stock?

Provide a clear and structured answer using this exact JSON format:

{{
    "recommendation": "BUY" | "SELL" | "HOLD",
    "confidence": 0.00 to 1.00,
    "reasoning": "Explain your technical analysis, and how (if at all) fundamentals support or contradict the technical signals."
}}
Respond with valid JSON only. Do not include any commentary outside of the JSON block.
"""
    return prompt

# LLM call helper

def call_ollama_llm(prompt: str) -> Dict[str, Any]:
    url = settings.OLLAMA_API_URL
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        logger.info(f"Sending prompt to Ollama model {settings.OLLAMA_MODEL} at {url}")
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        api_response_data = resp.json()
        logger.info(f"Raw Ollama response: {str(api_response_data)[:500]}")

        if 'response' in api_response_data:
            llm_output_str = api_response_data['response']
            match = re.search(r'\\{\\s*.*\\s*\\}', llm_output_str, re.DOTALL)
            if match:
                json_str = match.group(0)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse extracted JSON from LLM response: {e}. Extracted: {json_str}")
                    raise HTTPException(status_code=500, detail=f"Failed to parse JSON from LLM response: {json_str}")
            else:
                try:
                    return json.loads(llm_output_str)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse entire LLM response as JSON: {e}. Response: {llm_output_str}")
                    raise HTTPException(status_code=500, detail=f"LLM response was not valid JSON: {llm_output_str}")
        else:
            logger.error(f"No 'response' field in Ollama API output. Full response: {api_response_data}")
            raise HTTPException(status_code=500, detail="Invalid response structure from LLM: Missing 'response' field.")
            
    except requests.exceptions.Timeout:
        logger.error(f"LLM call timed out to {url}")
        raise HTTPException(status_code=504, detail="LLM call timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"LLM call failed: {e}")
        raise HTTPException(status_code=503, detail=f"LLM call failed: {e}")

class StockDataRequest(BaseModel):
    symbol: str
    timeframe: Optional[str] = settings.DEFAULT_TIMEFRAME
    date: Optional[str] = None

    @validator("timeframe")
    def validate_timeframe(cls, v):
        allowed = {"daily", "weekly", "monthly"}
        if v is not None and v not in allowed:
            raise ValueError(f"Invalid timeframe: {v}. Must be one of {allowed}")
        return v

class StockDataResponse(BaseModel):
    symbol: str
    technical_indicators: Dict[str, float]
    volume_features: Dict[str, Union[float, str]]
    fundamentals: Dict[str, Any]

class PredictRequest(BaseModel):
    symbol: str
    features: Dict[str, Any]

class PredictResponse(BaseModel):
    symbol: str
    recommendation: str
    confidence: float
    reasoning: str

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
        allowed = {"daily", "weekly", "monthly"}
        if request.timeframe not in allowed:
            raise HTTPException(status_code=422, detail=f"Invalid timeframe: {request.timeframe}. Must be one of {allowed}")
        logger.info(f"Starting data fetch for symbol: {request.symbol}, date: {request.date}")
        # Use fetch_price_data directly
        df = fetch_price_data(request.symbol, settings.ALPHA_VANTAGE_API_KEY, date=request.date)
        if df.empty:
            logger.warning(f"No data returned from fetch_price_data for symbol {request.symbol} and date {request.date}")
            raise HTTPException(status_code=404, detail=f"No data found for symbol {request.symbol} on the specified date or in recent history.")
        
        logger.info(f"Price data obtained for {request.symbol}. Shape: {df.shape}")
        
        # Filter to the specific date if provided, AFTER all data is fetched.
        target_df_for_indicators = df.copy()

        if request.date:
            try:
                target_date_dt = pd.to_datetime(request.date).date()
                target_df_for_indicators = df[df["date"] <= target_date_dt].copy()
                if target_df_for_indicators.empty:
                     raise HTTPException(status_code=404, detail=f"No data available up to {target_date_dt} for {request.symbol} to calculate indicators.")

                specific_date_df = df[df["date"] == target_date_dt].copy()
                if specific_date_df.empty:
                    raise HTTPException(status_code=404, detail=f"No data found for {request.symbol} specifically on {target_date_dt}")
                
            except ValueError:
                logger.error(f"Invalid date format provided: {request.date}")
                raise HTTPException(status_code=400, detail=f"Invalid date format: {request.date}. Use YYYY-MM-DD.")
        
        # Calculate indicators and features using the potentially larger historical df
        try:
            df_with_indicators = add_technical_indicators(target_df_for_indicators)
            logger.info(f"Technical indicators added. Columns: {df_with_indicators.columns.tolist()}")
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {request.symbol}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error calculating technical indicators: {str(e)}")
        
        # Select the specific date's data AFTER indicators are calculated on the series
        final_row_data = df_with_indicators.iloc[-1:]
        if request.date:
            target_date_dt = pd.to_datetime(request.date).date()
            final_row_data = df_with_indicators[df_with_indicators["date"] == target_date_dt]
            if final_row_data.empty:
                 raise HTTPException(status_code=404, detail=f"Data for {target_date_dt} disappeared after indicator calculation.")

        if final_row_data.empty:
            raise HTTPException(status_code=404, detail=f"No data available for {request.symbol} to extract features after indicator calculation.")

        try:
            volume_features = calculate_volume_features(df_with_indicators) 
            logger.info(f"Volume features calculated: {volume_features}")
        except Exception as e:
            logger.error(f"Error calculating volume features for {request.symbol}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error calculating volume features: {str(e)}")
            
        try:
            fundamentals = fetch_fundamentals(request.symbol, settings.ALPHA_VANTAGE_API_KEY)
            logger.info(f"Fundamentals fetched: {fundamentals}")
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {request.symbol}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error fetching fundamentals: {str(e)}")
        
        try:
            latest_indicators_row = final_row_data.iloc[-1]
            technical_indicators = {
                "latest_close": float(latest_indicators_row["close"]),
                "sma_5": float(latest_indicators_row["sma_5"]) if pd.notna(latest_indicators_row["sma_5"]) else 0.0,
                "ema_5": float(latest_indicators_row["ema_5"]) if pd.notna(latest_indicators_row["ema_5"]) else 0.0,
                "macd": float(latest_indicators_row["macd"]) if pd.notna(latest_indicators_row["macd"]) else 0.0,
                "macd_signal": float(latest_indicators_row["macd_signal"]) if pd.notna(latest_indicators_row["macd_signal"]) else 0.0,
                "macd_hist": float(latest_indicators_row["macd_hist"]) if pd.notna(latest_indicators_row["macd_hist"]) else 0.0,
                "bb_upper": float(latest_indicators_row["bb_upper"]) if pd.notna(latest_indicators_row["bb_upper"]) else 0.0,
                "bb_middle": float(latest_indicators_row["bb_middle"]) if pd.notna(latest_indicators_row["bb_middle"]) else 0.0,
                "bb_lower": float(latest_indicators_row["bb_lower"]) if pd.notna(latest_indicators_row["bb_lower"]) else 0.0,
                "open": float(latest_indicators_row["open"]) if "open" in latest_indicators_row and pd.notna(latest_indicators_row["open"]) else latest_indicators_row.get("close"),
                "high": float(latest_indicators_row["high"]) if "high" in latest_indicators_row and pd.notna(latest_indicators_row["high"]) else latest_indicators_row.get("close"),
                "low": float(latest_indicators_row["low"]) if "low" in latest_indicators_row and pd.notna(latest_indicators_row["low"]) else latest_indicators_row.get("close"),
                "volume": float(latest_indicators_row["volume"]) if "volume" in latest_indicators_row and pd.notna(latest_indicators_row["volume"]) else 0.0,
            }
            logger.info(f"Technical indicators prepared for response: {technical_indicators}")
        except IndexError:
             logger.error(f"Cannot extract latest_indicators_row for {request.symbol}, final_row_data might be empty.", exc_info=True)
             raise HTTPException(status_code=500, detail="Failed to extract features from processed data.")
        except Exception as e:
            logger.error(f"Error preparing technical indicators for response for {request.symbol}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error preparing technical indicators for response: {str(e)}")
        
        logger.info(f"Successfully completed data fetch for {request.symbol}")
        
        return StockDataResponse(
            symbol=request.symbol,
            technical_indicators=technical_indicators,
            volume_features=volume_features,
            fundamentals=fundamentals
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error fetching stock data for {request.symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    try:
        logger.info(f"Received predict request for {request.symbol} with features: {request.features}")
        prompt = format_llm_prompt(request.symbol, request.features)
        logger.info(f"Formatted LLM prompt for {request.symbol}:\\n{prompt}")
        
        llm_result = call_ollama_llm(prompt)
        logger.info(f"LLM result for {request.symbol}: {llm_result}")
        
        rec = llm_result.get("recommendation")
        conf = llm_result.get("confidence")
        reas = llm_result.get("reasoning")

        if not all([rec, isinstance(conf, (float, int)), reas]):
            logger.error(f"LLM response for {request.symbol} has missing or invalid fields: rec={rec}, conf={conf}, reas={reas}")
            raise HTTPException(status_code=500, detail="LLM response format is invalid or missing required fields.")

        return PredictResponse(
            symbol=request.symbol,
            recommendation=rec,
            confidence=float(conf),
            reasoning=reas
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during prediction for {request.symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during prediction process: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.LOG_LEVEL.lower() == "debug"
    )

