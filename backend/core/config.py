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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()