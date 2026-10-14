from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import os


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    APP_NAME: str = "TrackIT — Smart IT Service & Issue Management Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./trackit.db"

    # Security & JWT
    JWT_SECRET_KEY: str = "trackit_super_secret_development_key_change_in_production_9876543210"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # SLA Rules (in hours)
    SLA_LOW_HOURS: int = 72
    SLA_MEDIUM_HOURS: int = 48
    SLA_HIGH_HOURS: int = 24
    SLA_CRITICAL_HOURS: int = 4

    # Server Bindings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def get_sla_hours_for_priority(self, priority: str) -> int:
        mapping = {
            "LOW": self.SLA_LOW_HOURS,
            "MEDIUM": self.SLA_MEDIUM_HOURS,
            "HIGH": self.SLA_HIGH_HOURS,
            "CRITICAL": self.SLA_CRITICAL_HOURS,
        }
        return mapping.get(priority.upper(), self.SLA_MEDIUM_HOURS)


settings = Settings()
