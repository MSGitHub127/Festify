"""Centralized configuration for Festify.
Loads all tunables from environment variables with safe development defaults.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="FESTIFY_", extra="ignore")

    # App Identity
    app_name: str = "Festify — GenAI Event & Celebration Planner"
    environment: str = "development"  # development | staging | production
    version: str = "0.1.0"

    # Database & Enterprise Pooling
    database_url: str = "sqlite:///./festify.db"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_recycle: int = 3600

    # Security & Privacy
    secret_key: str = "dev-only-insecure-secret-change-me"
    token_expire_minutes: int = 120
    encryption_key: str = ""  # Fernet key for data at rest; generated if blank in dev
    allowed_origins: list[str] = ["*"]

    # Rate Limiting
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    redis_url: str = ""

    # Pluggable LLM Provider (mock for deterministic zero-cost offline tests, anthropic for live)
    llm_provider: str = "mock"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Uploads
    max_upload_bytes: int = 16 * 1024 * 1024  # 16 MB
    allowed_extensions: tuple[str, ...] = (".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".webp")


@lru_cache
def get_settings() -> Settings:
    return Settings()
