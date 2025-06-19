from dotenv import load_dotenv
load_dotenv()
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os

# Load environment variables from .env file

class Settings(BaseSettings):
    # API Keys
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    
    # Service Configuration
    SERVICE_NAME: str = "stock_data_fetching"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # API Configuration
    ALPHA_VANTAGE_BASE_URL: str = "https://www.alphavantage.co/query"
    OLLAMA_API_URL: str = os.getenv("OLLAMA_API_URL", "http://eass_ollama:11434/api/generate")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    
    # Default Stock Settings
    DEFAULT_SYMBOL: str = "AAPL"
    DEFAULT_TIMEFRAME: str = "daily"
    
    # Auth/JWT settings (added to match .env)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 