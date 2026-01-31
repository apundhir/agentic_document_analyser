from pydantic_settings import BaseSettings
from enum import Enum
import os

class Environment(str, Enum):
    DEV = "dev"
    PROD = "prod"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class Settings(BaseSettings):
    # Infrastructure
    ENV: Environment = Environment.DEV
    LOG_LEVEL: LogLevel = LogLevel.INFO
    
    # Preprocessing Service
    PREPROCESSING_HOST: str = "127.0.0.1"
    PREPROCESSING_PORT: int = 8001
    ENABLE_DESKEW: bool = True
    
    # Visual Service
    VISUAL_HOST: str = "127.0.0.1"
    VISUAL_PORT: int = 8002
    # Cloud Provider (Unified)
    FIREWORKS_API_KEY: str = ""
    FIREWORKS_MODEL: str = "accounts/fireworks/models/qwen3-vl-30b-a3b-instruct"

    # Orchestrator
    ORCHESTRATOR_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        # Helper to convert "PROD" (string) to Environment.PROD without fuss
        use_enum_values = True 

# Singleton instance
settings = Settings()
