from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Eco-Guard AI"
    API_V1_STR: str = "/api/v1"

    # Earth Engine
    EE_PROJECT_ID: str = "eco-guard-ai-489900"

    # Persistence
    DATABASE_URL: str = "sqlite:///./eco_guard.db"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Performance
    ANALYSIS_CACHE_TTL_SECONDS: int = 300
    ANALYSIS_CACHE_MAX_ITEMS: int = 1000

    # Alerting
    ALERT_EMAIL_TO: str = ""
    ALERT_WEBHOOK_URL: str = ""

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "eco-guard-ai@localhost"
    SMTP_STARTTLS: bool = True
    
    # CORS Security
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8501", "http://localhost:8000"]

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        level = value.upper().strip()
        if level not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {sorted(allowed)}")
        return level

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def normalize_cors_origins(cls, value: Any) -> list[str] | Any:
        if isinstance(value, str):
            parts = [item.strip() for item in value.split(",") if item.strip()]
            if parts:
                return parts
        return value

    @field_validator("ANALYSIS_CACHE_TTL_SECONDS", "ANALYSIS_CACHE_MAX_ITEMS")
    @classmethod
    def validate_positive_cache_settings(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("cache settings must be greater than 0")
        return value

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()