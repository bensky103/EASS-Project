from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Literal
import httpx
import logging
import uvicorn
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    open: float
    close: float
    high: float
    low: float
    volume: int
    sma_10: float
    rsi: float
    macd: float

    @validator('volume')
    def validate_volume(cls, v):
        if v < 0:
            raise ValueError('Volume cannot be negative')
        return v

    @validator('rsi')
    def validate_rsi(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('RSI must be between 0 and 100')
        return v

class PredictionRequest(BaseModel):
    symbol: str
    features: StockFeatures

class PredictionResponse(BaseModel):
    symbol: str
    recommendation: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence must be between 0 and 1')
        return v

def format_prompt(symbol: str, features: StockFeatures) -> str:
    """Format the stock features into a prompt for the LLM."""
    return f"""Given the following stock data for {symbol}:
- Open: {features.open:.2f}
- Close: {features.close:.2f}
- High: {features.high:.2f}
- Low: {features.low:.2f}
- Volume: {features.volume:,}
- 10-day SMA: {features.sma_10:.2f}
- RSI: {features.rsi:.1f}
- MACD: {features.macd:.2f}

Should I BUY, SELL, or HOLD? Explain your reasoning using technical analysis.
Provide your response in the following JSON format:
{{
    "recommendation": "BUY|SELL|HOLD",
    "confidence": 0.XX,
    "reasoning": "Your analysis here"
}}"""

async def call_ollama(prompt: str) -> Dict[str, Any]:
    """Call the Ollama API to get a prediction."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "http://eass_ollama:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail="Ollama service is not reachable. Please ensure it's running on eass_ollama:11434"
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
        logger.info(f"Raw response from Ollama: {response_text}")
        
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
    return {"status": "healthy", "service": "stock-prediction-llm"}

@app.post("/predict", response_model=PredictionResponse)
async def predict_stock(request: PredictionRequest):
    """
    Generate a stock prediction using LLaMA 3 via Ollama
    """
    try:
        logger.info(f"Generating prediction for {request.symbol}")
        
        # Format the prompt
        prompt = format_prompt(request.symbol, request.features)
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
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "llm_service:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 