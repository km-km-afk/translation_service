'''Purpose: Centralized configuration for the entire application
What it does:

Reads environment variables from .env file
Provides default values
Makes configuration accessible throughout the app
Validates configuration on startup'''


from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    APP_NAME: str = "Translation Microservice"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    MAX_TEXT_LENGTH: int = 1000
    MAX_BULK_SIZE: int = 50
    
    #Google Translate API (i have built use mock API)
    USE_GOOGLE_API: bool = False
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_PROJECT_ID: Optional[str] = None
    
    #Database
    USE_DATABASE: bool = True
    DATABASE_PATH: str = "translation_logs.db"
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


#Initialize settings
settings = Settings()