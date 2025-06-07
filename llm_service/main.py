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
    
    time_frame_instruction = "Your analysis should determine the most appropriate time frame for the prediction (e.g., next few days, 1 week, 1 month)."
    if time_frame:
        time_frame_instruction = f"Your analysis should be for the following time frame: {time_frame}."

    prompt = f"""Stock Symbol: {symbol}\n\n[TECHNICAL INDICATORS]\nLatest Close: {features.latest_close}\nSMA 5: {features.sma_5}\nEMA 5: {features.ema_5}\nMACD: {features.macd}\nMACD Signal: {features.macd_signal}\nMACD Histogram: {features.macd_hist}\nBollinger Bands - Upper: {features.bb_upper}, Middle: {features.bb_middle}, Lower: {features.bb_lower}\nOpen: {features.open}\nHigh: {features.high}\nLow: {features.low}\nVolume: {features.volume}\n\n[VOLUME FEATURES]\nLatest Volume: {features.latest_volume}\nAverage Volume: {features.volume_avg}\nVolume Spike: {features.volume_spike}\nOn-Balance Volume (OBV): {features.obv}\nVolume SMA: {features.volume_sma}\nVolume Ratio: {features.volume_ratio}\nVolume Trend: {features.volume_trend}\n\n[FUNDAMENTALS]\nMarket Cap: {features.market_cap}\nP/E Ratio: {features.pe_ratio}\nDividend Yield: {features.dividend_yield}\nBeta: {features.beta}\n"""
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
[Provide a day-by-day price prediction for the specified time frame. Each prediction MUST be on a new line, formatted as 'Day X: PRICE' or 'YYYY-MM-DD: PRICE'.]
REASONING: [Your detailed analysis here. This can span multiple lines. Ensure subsequent lines of reasoning do not start with a keyword.]

Example of the EXACT required format:
RECOMMENDATION: BUY
CONFIDENCE: 0.80
TIME_FRAME: Next 5 trading days
PRICE_PREDICTIONS:
Day 1: 175.50
Day 2: 176.20
Day 3: 175.80
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

        if stripped_line.upper().startswith("RECOMMENDATION:"):
            recommendation_str = stripped_line[len("RECOMMENDATION:"):].strip()
            parsing_state = None
        elif stripped_line.upper().startswith("CONFIDENCE:"):
            confidence_str = stripped_line[len("CONFIDENCE:"):].strip()
            parsing_state = None
        elif stripped_line.upper().startswith("TIME_FRAME:"):
            time_frame_str = stripped_line[len("TIME_FRAME:"):].strip()
            parsing_state = None
        elif stripped_line.upper().startswith("PRICE_PREDICTIONS:"):
            # This line only serves as a marker, the content is on the next lines
            parsing_state = "predictions"
        elif stripped_line.upper().startswith("REASONING:"):
            reasoning_lines.append(stripped_line[len("REASONING:"):].strip())
            parsing_state = "reasoning"
        elif parsing_state == "predictions":
            # Any line after PRICE_PREDICTIONS: and before REASONING: is a prediction
            price_prediction_lines.append(stripped_line)
        elif parsing_state == "reasoning":
            # If we are in parsing_reasoning mode, append the whole line
            reasoning_lines.append(stripped_line)
        elif recommendation_str and confidence_str and time_frame_str and stripped_line:
            # Fallback for reasoning if it was not explicitly prefixed
            logger.warn(f"REASONING: prefix missing. Assuming line starts reasoning: '{stripped_line[:100]}...'")
            reasoning_lines.append(stripped_line)
            parsing_state = "reasoning"

    # --- Validation ---
    if recommendation_str is None:
        logger.error(f"Could not parse RECOMMENDATION. Raw response (first 500 chars): {response_text[:500]}")
        raise HTTPException(status_code=500, detail="LLM response missing RECOMMENDATION.")
    
    recommendation = None
    valid_recommendations = ["BUY", "SELL", "HOLD"]
    # Try to find a valid recommendation even if there's extra text or wrong casing
    rec_upper = recommendation_str.upper()
    for valid_rec in valid_recommendations:
        if valid_rec in rec_upper:
            recommendation = valid_rec
            break
    
    if recommendation is None:
        logger.error(f"Invalid RECOMMENDATION value: '{recommendation_str}'. Expected one of {valid_recommendations}. Raw response: {response_text[:500]}")
        raise HTTPException(status_code=500, detail=f"Invalid RECOMMENDATION value: '{recommendation_str}'. Expected one of {valid_recommendations}.")

    if confidence_str is None:
        logger.error(f"Could not parse CONFIDENCE. Raw response (first 500 chars): {response_text[:500]}")
        raise HTTPException(status_code=500, detail="LLM response missing CONFIDENCE.")
    
    confidence = None
    try:
        # Attempt to extract a float from the string, e.g., "0.75", "0.7 whatever", "approx 0.8"
        # This regex looks for a number like 0.x, .x, 0, 1
        match = re.search(r'([01]?\.\d+|[01])', confidence_str)
        if match:
            confidence = float(match.group(1))
            if not (0.0 <= confidence <= 1.0):
                logger.error(f"CONFIDENCE value {confidence} out of range (0-1). Original str: '{confidence_str}'. Raw response: {response_text[:500]}")
                raise ValueError("Confidence out of range")
        else:
            raise ValueError("No float-like number found in confidence string")
            
    except ValueError as e:
        logger.error(f"Invalid CONFIDENCE value: '{confidence_str}'. Error: {e}. Raw response: {response_text[:500]}")
        raise HTTPException(status_code=500, detail=f"Invalid CONFIDENCE value: '{confidence_str}'. Must be a number between 0.0 and 1.0.")

    if not time_frame_str:
        logger.error(f"Could not parse TIME_FRAME. Raw response: {response_text[:500]}")
        raise HTTPException(status_code=500, detail="LLM response missing TIME_FRAME.")

    price_predictions = {}
    if not price_prediction_lines:
        logger.error(f"Could not parse PRICE_PREDICTIONS or it is empty. Raw response: {response_text[:500]}")
        raise HTTPException(status_code=500, detail="LLM response missing PRICE_PREDICTIONS or it is empty.")

    for line in price_prediction_lines:
        # This regex handles formats like "Day 1: 150.50", "2024-07-26: 155.0", etc.
        match = re.match(r'([^:]+):\s*([\d\.]+)', line.strip())
        if match:
            key = match.group(1).strip()
            try:
                value = float(match.group(2))
                price_predictions[key] = value
            except ValueError:
                logger.warn(f"Could not parse price value in PRICE_PREDICTIONS line: '{line}'")
        else:
            logger.warn(f"Skipping malformed PRICE_PREDICTIONS line: '{line}'")

    if not price_predictions:
        logger.error(f"Failed to parse any valid price predictions from lines: {price_prediction_lines}. Raw response: {response_text[:500]}")
        raise HTTPException(status_code=500, detail="LLM response contained no valid PRICE_PREDICTIONS.")

    reasoning = " ".join(reasoning_lines).strip()
    if not reasoning: # Check if reasoning_lines was empty or only contained whitespace
        logger.error(f"Could not parse REASONING or reasoning is empty. Raw response (first 500 chars): {response_text[:500]}")
        raise HTTPException(status_code=500, detail="LLM response missing REASONING or reasoning is empty.")
        
    logger.info(f"Successfully parsed LLM response: Rec: {recommendation}, Conf: {confidence}, TF: {time_frame_str}, Predictions: {len(price_predictions)} found.")
    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "reasoning": reasoning,
        "time_frame": time_frame_str,
        "price_predictions": price_predictions
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
        
        logger.info(f"Features for {request.symbol}: {features.model_dump_json(indent=2)}")
        
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