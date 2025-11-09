"""Configuration management for the AG2 backend."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    
    # Application
    FRONTEND_URL: str = "https://ag2-predictive-state-editor.vercel.app"
    PORT: int = 8080
    ENVIRONMENT: str = "production"
    
    # LLM Configuration
    PRIMARY_LLM: str = "gemini"
    MODEL_NAME: str = "gemini-1.5-flash"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
