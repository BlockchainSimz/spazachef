"""Application configuration for SpazaChef."""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "SpazaChef API"
    ENV: str = "production"
    DEBUG: bool = False

    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    DATABASE_URL: str = ""
    REDIS_URL: str = ""

    JWT_SECRET: str = Field(default="", repr=False)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    ANTHROPIC_API_KEY: str = Field(default="", repr=False)
    ANTHROPIC_MODEL: str = "claude-3-5-haiku-latest"
    ANTHROPIC_TIMEOUT_SECONDS: float = 30.0

    PAYFAST_MERCHANT_ID: str = Field(default="", repr=False)
    PAYFAST_MERCHANT_KEY: str = Field(default="", repr=False)
    PAYFAST_MODE: str = "test"

    OZOW_API_KEY: str = Field(default="", repr=False)
    OZOW_API_SECRET: str = Field(default="", repr=False)

    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
