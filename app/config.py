"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Bland AI
    BLAND_API_KEY: str = ""
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # Resend (Email)
    RESEND_API_KEY: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # App Configuration
    MANAGER_EMAIL: str = "manager@property.com"
    API_BASE_URL: str = "http://localhost:8000"
    PROPERTY_NAME: str = "Sunset Apartments"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
