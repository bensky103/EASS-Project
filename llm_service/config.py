from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # Service settings
    SERVICE_NAME: str = "stock-prediction-llm"
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Ollama settings
    OLLAMA_API_URL: str = "http://eass_ollama:11434/api/generate"
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_TIMEOUT: int | None = 6000
    
    # Auth/JWT settings (added to match .env)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

settings = get_settings() 