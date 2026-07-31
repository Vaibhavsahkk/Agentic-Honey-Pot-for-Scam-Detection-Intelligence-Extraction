"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    API_KEY: str = "default-dev-key"
    PORT: int = 8010
    
    # LLM Provider Settings
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LLM_PROVIDER: Literal["openai", "groq", "fallback"] = "fallback"
    LLM_MODEL: str = "llama3-70b-8192"
    
    # GUVI Hackathon
    GUVI_CALLBACK_URL: str = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    # System Settings
    MAX_CONVERSATION_TURNS: int = 15
    MIN_INTELLIGENCE_THRESHOLD: int = 2
    DEBUG_MODE: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
