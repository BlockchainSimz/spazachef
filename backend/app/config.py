"""Configuration management for SpazaChef API"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "SpazaChef API"
    DEBUG: bool = True
    ENV: str = "development"
    
    # Database - Direct PostgreSQL Connection
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/postgres"
    )
    
    # Supabase (REST API)
    SUPABASE_URL: str = "https://itkovoagalodjqfjvmlp.supabase.co"
    SUPABASE_ANON_KEY: str = "sb_publishable_aQGYuHXVJ7xah8ZXlw0Bhw_P8uBOBnf"
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # PayFast
    PAYFAST_MERCHANT_ID: str = ""
    PAYFAST_MERCHANT_KEY: str = ""
    PAYFAST_MODE: str = "test"
    
    # Ozow
    OZOW_API_KEY: str = ""
    OZOW_API_SECRET: str = ""
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://spazachef.vercel.app",
    ]
    
    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
