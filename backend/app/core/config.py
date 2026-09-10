import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "VARUNA"
    PROJECT_TITLE: str = "AI-Powered Marine Intelligence"
    TAGLINE: str = "Transforming Marine Data into Intelligent Decisions."
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    SECRET_KEY: str = "change_me_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = "sqlite:///./varuna.db"

    OPENMETEO_BASE_URL: str = "https://marine-api.open-meteo.com/v1"
    OPENMETEO_WEATHER_URL: str = "https://api.open-meteo.com/v1"
    COPERNICUS_USERNAME: str = ""
    COPERNICUS_PASSWORD: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    DEFAULT_OPERATIONAL_MODE: str = "LIVE" # LIVE, DEMO, HYBRID

    # ── Notification Services ────────────────────────────────────────────────
    # Email (SMTP)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "alerts@varuna.gov.in"
    SMTP_USE_TLS: bool = True

    # SMS (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""

    # Push Notifications (Firebase Cloud Messaging)
    FCM_SERVER_KEY: str = ""
    FCM_PROJECT_ID: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
