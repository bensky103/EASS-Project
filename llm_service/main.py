from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Literal
import httpx
import uvicorn
from datetime import datetime

from .config import settings
from .logger import logger

app = FastAPI(
    title="Stock Prediction LLM Service",
    description="Service for generating stock predictions using LLaMA 3 via Ollama",
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

class StockFeatures(BaseModel):
    # technical_indicators
    latest_close: float
    sma_5: float
    ema_5: float
    macd: float
    macd_signal: float
    macd_hist: float
    bb_upper: float
    bb_middle: float
    bb_lower: float
    open: float
    high: float
    low: float
    volume: int
    # volume_features
    latest_volume: int
    volume_avg: float
    volume_spike: int
    obv: int
    volume_sma: float
    volume_ratio: float
    volume_trend: str
    # fundamentals
    market_cap: int
    pe_ratio: float
    dividend_yield: float
    beta: float

    @field_validator('volume')
    @classmethod
    def validate_volume(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Volume cannot be negative')
        return v

    @field_validator('rsi')
    @classmethod
    def validate_rsi(cls, v: float) -> float:
        if not 0 <= v <= 100:
            raise ValueError('RSI must be between 0 and 100')
        return v

class PredictionRequest(BaseModel):
    symbol: str
    features: StockFeatures | None = None

class PredictionResponse(BaseModel):
    symbol: str
    recommendation: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError('Confidence must be between 0 and 1')
        return v

def format_prompt(symbol: str, features: StockFeatures) -> str:
    """Format all features into a prompt for the LLM."""
    return f"""Stock Symbol: {symbol}\n\n[TECHNICAL INDICATORS]\nLatest Close: {features.latest_close}\nSMA 5: {features.sma_5}\nEMA 5: {features.ema_5}\nMACD: {features.macd}\nMACD Signal: {features.macd_signal}\nMACD Histogram: {features.macd_hist}\nBollinger Bands - Upper: {features.bb_upper}, Middle: {features.bb_middle}, Lower: {features.bb_lower}\nOpen: {features.open}\nHigh: {features.high}\nLow: {features.low}\nVolume: {features.volume}\n\n[VOLUME FEATURES]\nLatest Volume: {features.latest_volume}\nAverage Volume: {features.volume_avg}\nVolume Spike: {features.volume_spike}\nOn-Balance Volume (OBV): {features.obv}\nVolume SMA: {features.volume_sma}\nVolume Ratio: {features.volume_ratio}\nVolume Trend: {features.volume_trend}\n\n[FUNDAMENTALS]\nMarket Cap: {features.market_cap}\nP/E Ratio: {features.pe_ratio}\nDividend Yield: {features.dividend_yield}\nBeta: {features.beta}\n\nInstructions:\nAnalyze the stock using all the above features. Provide a recommendation (BUY, SELL, HOLD), a confidence score (0-1), and a detailed reasoning.\n\nRespond in this JSON format:\n{{\n    \"recommendation\": \"BUY|SELL|HOLD\",\n    \"confidence\": 0.XX,\n    \"reasoning\": \"Your analysis here\"\n}}"""

async def call_ollama(prompt: str) -> Dict[str, Any]:
    """Call the Ollama API to get a prediction."""
    async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
        try:
            response = await client.post(
                settings.OLLAMA_API_URL,
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail="Ollama service is not reachable. Please ensure it's running on localhost:11434"
            )
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calling Ollama API: {str(e)}"
            )

def parse_llm_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Parse and validate the LLM response."""
    try:
        # Extract the response text from Ollama's response
        response_text = response.get("response", "")
        
        # Find the JSON part of the response
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No valid JSON found in response")
            
        json_str = response_text[start_idx:end_idx]
        import json
        parsed = json.loads(json_str)
        
        # Validate the parsed response
        if "recommendation" not in parsed or "confidence" not in parsed or "reasoning" not in parsed:
            raise ValueError("Missing required fields in LLM response")
            
        if parsed["recommendation"] not in ["BUY", "SELL", "HOLD"]:
            raise ValueError("Invalid recommendation value")
            
        if not isinstance(parsed["confidence"], (int, float)) or not 0 <= parsed["confidence"] <= 1:
            raise ValueError("Invalid confidence value")
            
        return parsed
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Failed to parse LLM response as JSON"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid LLM response format: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.SERVICE_NAME}

@app.post("/predict", response_model=PredictionResponse)
async def predict_stock(request: PredictionRequest):
    """
    Generate a stock prediction using LLaMA 3 via Ollama. If features are not provided, fetch them from the stock data service.
    """
    try:
        logger.info(f"Generating prediction for {request.symbol}")
        features = request.features
        if features is None:
            # Fetch features from stock data service
            stock_data_url = "http://eass_stock_data:8000/fetch"
            async with httpx.AsyncClient(timeout=30) as client:
                fetch_resp = await client.post(stock_data_url, json={"symbol": request.symbol})
                fetch_resp.raise_for_status()
                data = fetch_resp.json()
                # Combine all features into a single dict
                combined = {}
                combined.update(data.get("technical_indicators", {}))
                combined.update(data.get("volume_features", {}))
                combined.update(data.get("fundamentals", {}))
                # Map to StockFeatures
                features = StockFeatures(
                    latest_close=combined.get("latest_close", 0.0),
                    sma_5=combined.get("sma_5", 0.0),
                    ema_5=combined.get("ema_5", 0.0),
                    macd=combined.get("macd", 0.0),
                    macd_signal=combined.get("macd_signal", 0.0),
                    macd_hist=combined.get("macd_hist", 0.0),
                    bb_upper=combined.get("bb_upper", 0.0),
                    bb_middle=combined.get("bb_middle", 0.0),
                    bb_lower=combined.get("bb_lower", 0.0),
                    open=combined.get("open", 0.0),
                    high=combined.get("high", 0.0),
                    low=combined.get("low", 0.0),
                    volume=int(combined.get("volume", 0)),
                    latest_volume=int(combined.get("latest_volume", 0)),
                    volume_avg=combined.get("volume_avg", 0.0),
                    volume_spike=int(combined.get("volume_spike", 0)),
                    obv=int(combined.get("obv", 0)),
                    volume_sma=combined.get("volume_sma", 0.0),
                    volume_ratio=combined.get("volume_ratio", 0.0),
                    volume_trend=combined.get("volume_trend", ""),
                    market_cap=int(combined.get("market_cap", 0)),
                    pe_ratio=combined.get("pe_ratio", 0.0),
                    dividend_yield=combined.get("dividend_yield", 0.0),
                    beta=combined.get("beta", 0.0)
                )
        # Format the prompt
        prompt = format_prompt(request.symbol, features)
        logger.info("Prompt formatted successfully")
        # Call Ollama
        llm_response = await call_ollama(prompt)
        logger.info("Received response from Ollama")
        # Parse and validate the response
        parsed_response = parse_llm_response(llm_response)
        logger.info(f"Parsed LLM response: {parsed_response}")
        # Create the response
        response = PredictionResponse(
            symbol=request.symbol,
            recommendation=parsed_response["recommendation"],
            confidence=parsed_response["confidence"],
            reasoning=parsed_response["reasoning"]
        )
        logger.info(f"Successfully generated prediction for {request.symbol}")
        return response
    except Exception as e:
        logger.error(f"Error generating prediction for {request.symbol}: {str(e)}")
        logger.exception("Full traceback:")
        import httpx
        if isinstance(e, httpx.ConnectError):
            raise HTTPException(status_code=503, detail="Ollama service is not reachable. Please ensure it's running on localhost:11434")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    ) 