from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Literal
import httpx
import uvicorn
from datetime import datetime
import json
import re

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

class PredictionRequest(BaseModel):
    symbol: str
    features: StockFeatures | None = None
    time_frame: str | None = Field(None, description="The desired time frame for the prediction (e.g., 'next 5 trading days').")

class PredictionResponse(BaseModel):
    symbol: str
    recommendation: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    time_frame: str = Field(..., description="The time frame for which the prediction is valid (e.g., 'Next 5 trading days').")
    price_predictions: Dict[str, float] = Field(..., description="A dictionary of predicted prices, where keys are dates or day identifiers (e.g., 'Day 1', '2024-07-26') and values are the predicted prices.")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError('Confidence must be between 0 and 1')
        return v

def format_prompt(symbol: str, features: StockFeatures, time_frame: str | None = None, news_sentiment: dict = None) -> str:
    """Format all features into a prompt for the LLM, including news sentiment and a desired time frame."""
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    time_frame_instruction = "Your analysis should determine the most appropriate time frame for the prediction (e.g., next few days, 1 week, 1 month)."
    if time_frame:
        time_frame_instruction = f"Your analysis should be for the following time frame: {time_frame}."

    prompt = f"""Current Date: {current_date}
Stock Symbol: {symbol}\n\n[TECHNICAL INDICATORS]\nLatest Close: {features.latest_close}\nSMA 5: {features.sma_5}\nEMA 5: {features.ema_5}\nMACD: {features.macd}\nMACD Signal: {features.macd_signal}\nMACD Histogram: {features.macd_hist}\nBollinger Bands - Upper: {features.bb_upper}, Middle: {features.bb_middle}, Lower: {features.bb_lower}\nOpen: {features.open}\nHigh: {features.high}\nLow: {features.low}\nVolume: {features.volume}\n\n[VOLUME FEATURES]\nLatest Volume: {features.latest_volume}\nAverage Volume: {features.volume_avg}\nVolume Spike: {features.volume_spike}\nOn-Balance Volume (OBV): {features.obv}\nVolume SMA: {features.volume_sma}\nVolume Ratio: {features.volume_ratio}\nVolume Trend: {features.volume_trend}\n\n[FUNDAMENTALS]\nMarket Cap: {features.market_cap}\nP/E Ratio: {features.pe_ratio}\nDividend Yield: {features.dividend_yield}\nBeta: {features.beta}\n"""
    if news_sentiment:
        prompt += "\\n[NEWS SENTIMENT]\\n"
        prompt += f"Sentiment Score: {news_sentiment.get('sentiment_score', 'N/A')}\\n"
        prompt += f"Sentiment Counts: {news_sentiment.get('sentiment_counts', {})}\\n"
        for h in news_sentiment.get('headlines', []):
            prompt += f"- {h.get('title', '')} (Sentiment: {h.get('sentiment', '')})\\n"
    
    prompt += f""" 

Instructions:
Analyze the stock using all the above features, including news sentiment.
{time_frame_instruction}
Your entire response MUST be plain text. Do NOT use JSON or any other structured format.
Return your response strictly in the following KEY: VALUE format, with each item on a new line:
RECOMMENDATION: [BUY, SELL, or HOLD]
CONFIDENCE: [a number between 0.0 and 1.0, e.g., 0.75]
TIME_FRAME: [The time frame for your prediction, e.g., "Next 5 trading days"]
PRICE_PREDICTIONS:
[Provide a day-by-day price prediction for the specified time frame. Each prediction MUST be on a new line, formatted as 'Day X: PRICE'. For predictions over a number of days, use 'YYYY-MM-DD' format.]
REASONING: [Your detailed analysis here. This can span multiple lines. Ensure subsequent lines of reasoning do not start with a keyword.]

Example of the EXACT required format (change the dates in the PRICE_PREDICTIONS to the current date):
RECOMMENDATION: BUY
CONFIDENCE: 0.80
TIME_FRAME: Next 5 trading days
PRICE_PREDICTIONS:
2025/06/08: 175.50
2025/06/09: 176.20
2025/06/10: 175.80
2025/06/11: 176.50
2025/06/12: 177.00
REASONING: The stock shows strong bullish signals and is expected to rise.
The technical indicators support a continued upward trend.

Important:
- Each keyword (RECOMMENDATION, CONFIDENCE, TIME_FRAME, REASONING) must be at the beginning of its line.
- PRICE_PREDICTIONS must be on its own line, followed by the day-by-day predictions on subsequent lines.
- The REASONING keyword and its value must start on a new line AFTER all price predictions.
- Do not include any other text, explanations, or conversational filler before the first keyword or after the reasoning.
- The REASONING can be multi-line. All lines after "REASONING: " are part of the reasoning.
"""
    return prompt

async def call_ollama(prompt: str) -> Dict[str, Any]:
    """Call the Ollama API to get a prediction."""
    async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
        try:
            response = await client.post(
                settings.OLLAMA_API_URL,
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            try:
                return response.json() # Primary attempt
            except json.JSONDecodeError as e_json_parse: # More specific exception for when response.json() fails
                logger.warn(f"response.json() failed ({e_json_parse}). Attempting to parse response.text as a stream of JSON objects. Raw response text (first 1000 chars):\n{response.text[:1000]}...")

                accumulated_response_str = ""
                # Default values for the wrapper object
                model_name = settings.OLLAMA_MODEL
                created_time = datetime.utcnow().isoformat() + "Z"
                
                lines = response.text.strip().split('\n')

                if not response.text.strip():
                    logger.error(f"Fallback stream parsing: response.text is empty or only whitespace. Original httpx error: {e_json_parse}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Ollama API request failed ({e_json_parse}) and response body was empty."
                    )

                any_chunk_processed_successfully = False
                for i, line_str in enumerate(lines):
                    line_content = line_str.strip()
                    if not line_content:
                        continue
                    
                    try:
                        line_json = json.loads(line_content)
                        any_chunk_processed_successfully = True
                        accumulated_response_str += line_json.get("response", "")
                        
                        # Update model_name and created_time from the chunk if available
                        if "model" in line_json: model_name = line_json["model"]
                        if "created_at" in line_json: created_time = line_json["created_at"]
                        
                    except json.JSONDecodeError:
                        logger.warn(f"Fallback stream parsing: Skipping non-JSON line: '{line_content[:200]}...'")
                        # If this is the only line and nothing has been accumulated,
                        # it might be a plain text response from Ollama (e.g., an error message).
                        if len(lines) == 1 and not accumulated_response_str:
                            accumulated_response_str = line_content
                            logger.info(f"Fallback stream parsing: Treating single non-JSON line as response content: '{accumulated_response_str[:200]}...'")
                            any_chunk_processed_successfully = True # Mark as processed to avoid later error
                            break # No more lines to process in this case
                
                if not any_chunk_processed_successfully and not accumulated_response_str:
                    logger.error(f"Fallback stream parsing: Failed to extract any usable content from response.text. Original httpx error: {e_json_parse}. Response text (first 1000 chars): {response.text[:1000]}...")
                    raise HTTPException(status_code=500, detail=f"Ollama API request failed: ({e_json_parse}) and could not parse response from Ollama stream.")

                # Construct the dictionary that parse_llm_response expects
                final_structured_response = {
                    "model": model_name,
                    "created_at": created_time,
                    "response": accumulated_response_str,
                    "done": True # We assume it's done after processing all available text
                }
                
                logger.info(f"Fallback stream parsing: Reconstructed Ollama response. Content (first 100 chars of 'response' field): '{accumulated_response_str[:100]}...'")
                return final_structured_response
        except httpx.ConnectError as e_connect:
            logger.error(f"Cannot connect to Ollama service: {e_connect}")
            raise HTTPException(
                status_code=503,
                detail=f"Ollama service is not reachable at {settings.OLLAMA_API_URL}. Ensure it's running."
            )
        except httpx.ReadTimeout as e_read_timeout:
            logger.error(f"Ollama API request timed out after {settings.OLLAMA_TIMEOUT}s: {e_read_timeout}")
            raise HTTPException(
                status_code=504,
                detail=f"Ollama service timed out responding to the request after {settings.OLLAMA_TIMEOUT}s."
            )
        except httpx.HTTPStatusError as e_http_status:
            logger.error(f"Ollama API request failed with status {e_http_status.response.status_code}: {e_http_status.response.text}")
            raise HTTPException(
                status_code=e_http_status.response.status_code,
                detail=f"Error calling Ollama API: Status {e_http_status.response.status_code}. Response: {e_http_status.response.text[:500]}"
            )
        except httpx.HTTPError as e_http: # Catch other httpx errors
            logger.error(f"An HTTP error occurred while calling Ollama API: {str(e_http)}")
            raise HTTPException(
                status_code=500, # Generic server error for other HTTP issues
                detail=f"Error calling Ollama API: {str(e_http)}"
            )

def parse_llm_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse and validate the LLM response from a line-delimited format."""
    response_text = response_data.get("response")

    if not isinstance(response_text, str) or not response_text.strip():
        logger.error(f"LLM response text is missing or empty. Data: {response_data}")
        raise HTTPException(status_code=500, detail="LLM returned no parsable content.")

    lines = response_text.strip().split('\n')
    
    recommendation_str = None
    confidence_str = None
    time_frame_str = None
    price_prediction_lines = []
    reasoning_lines = []
    
    parsing_state = None  # Can be "predictions" or "reasoning"

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        # Use regex to handle both 'Key: Value' and multiline values
        match_key_value = re.match(r'^([A-Z_]+):\s*(.*)', stripped_line)

        if match_key_value:
            key = match_key_value.group(1)
            value = match_key_value.group(2).strip()
            parsing_state = None  # Reset state on a new key

            if key == 'RECOMMENDATION':
                recommendation_str = value
            elif key == 'CONFIDENCE':
                confidence_str = value
            elif key == 'TIME_FRAME':
                time_frame_str = value
            elif key == 'PRICE_PREDICTIONS':
                parsing_state = 'predictions'
            elif key == 'REASONING':
                parsing_state = 'reasoning'
                if value:  # Capture reasoning on the same line
                    reasoning_lines.append(value)
        elif parsing_state == 'predictions':
            price_prediction_lines.append(stripped_line)
        elif parsing_state == 'reasoning':
            reasoning_lines.append(stripped_line)

    # Validate required fields
    if not all([recommendation_str, confidence_str, time_frame_str]):
        raise HTTPException(
            status_code=500,
            detail=f"LLM response was missing one or more required fields: RECOMMENDATION, CONFIDENCE, or TIME_FRAME. Raw response: {response_text}"
        )

    # Process and validate parsed values
    try:
        recommendation = recommendation_str.upper()
        if recommendation not in ["BUY", "SELL", "HOLD"]:
            raise ValueError("Recommendation must be BUY, SELL, or HOLD.")
        
        confidence = float(confidence_str)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0.")

        price_predictions = {}
        # Regex to capture Day X, YYYY-MM-DD, or MM/DD/YYYY formats
        prediction_regex = re.compile(r'^(Day\s+\d+|(?:\d{4}-\d{2}-\d{2})|(?:\d{2}/\d{2}/\d{4})):\s*(\d+\.?\d*)')
        for pred_line in price_prediction_lines:
            match = prediction_regex.match(pred_line.strip())
            if match:
                day_key = match.group(1)
                price_val = float(match.group(2))
                price_predictions[day_key] = price_val

        if not price_predictions and price_prediction_lines:
             logger.warning(f"Could not parse any price predictions from lines: {price_prediction_lines}. Raw response: {response_text}")


        reasoning = " ".join(reasoning_lines).strip()
        if not reasoning:
            raise ValueError("Reasoning cannot be empty.")

    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing LLM response fields: {e}. Raw response: {response_text}"
        )

    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "time_frame": time_frame_str,
        "price_predictions": price_predictions,
        "reasoning": reasoning
    }

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
        data = {}  # Initialize data to an empty dict
        news_sentiment = None
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
                news_sentiment = data.get("news_sentiment", {})
                # Add new features
                combined["advanced_news_sentiment"] = data.get("advanced_news_sentiment", {})
                combined["extended_fundamentals"] = data.get("extended_fundamentals", {})
                combined["technical_indicators_ext"] = data.get("technical_indicators_ext", {})
                combined["volume_features_ext"] = data.get("volume_features_ext", {})
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
        # Log all features including new ones
        all_features = {
            **features.model_dump(),
            "advanced_news_sentiment": data.get("advanced_news_sentiment", {}),
            "extended_fundamentals": data.get("extended_fundamentals", {}),
            "technical_indicators_ext": data.get("technical_indicators_ext", {}),
            "volume_features_ext": data.get("volume_features_ext", {})
        }
        logger.info(f"Features for {request.symbol}: {json.dumps(all_features, indent=2)}")
        
        # Format the prompt
        prompt = format_prompt(request.symbol, features, request.time_frame, news_sentiment)
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
            reasoning=parsed_response["reasoning"],
            time_frame=parsed_response["time_frame"],
            price_predictions=parsed_response["price_predictions"]
        )
        logger.info(f"Successfully generated prediction for {request.symbol}")
        return response
    except Exception as e:
        logger.error(f"Error generating prediction for {request.symbol}: {str(e)}")
        logger.exception("Full traceback:")
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