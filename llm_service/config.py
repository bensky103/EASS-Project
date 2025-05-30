from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""
    
    # Service settings
    SERVICE_NAME: str = "stock-prediction-llm"
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: str = ""
    
    # Ollama settings
    OLLAMA_API_URL: str = "http://localhost:11434/api/generate"
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_TIMEOUT: int = 30
    
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