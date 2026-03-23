import os


class Settings:
    PROJECT_NAME: str = "Eco-Guard AI"
    API_V1_STR: str = "/api/v1"

    # Earth Engine
    EE_PROJECT_ID: str = os.getenv("EE_PROJECT_ID", "eco-guard-ai-489900")

    # Persistence
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mongodb+srv://masterchandan24_db_user:UhWe12JyVfIilfdY@cluster0.gfxjnjc.mongodb.net/")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Alerting
    ALERT_EMAIL_TO: str = os.getenv("ALERT_EMAIL_TO", "")
    ALERT_WEBHOOK_URL: str = os.getenv("ALERT_WEBHOOK_URL", "")

    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "eco-guard-ai@localhost")
    SMTP_STARTTLS: bool = os.getenv("SMTP_STARTTLS", "true").lower() == "true"


settings = Settings()