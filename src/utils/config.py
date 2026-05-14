"""
Application settings loaded from environment variables.

Uses ``pydantic-settings`` so every field can be overridden via the
environment or a ``.env`` file without changing code.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """DERMS application settings.

    All fields are populated from environment variables (case-insensitive).
    A ``.env`` file is automatically read when present.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./derms_dev.db",
        description="SQLAlchemy async database URL",
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # API security
    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for JWT signing — MUST be overridden in production",
    )
    api_key: str = Field(default="", description="Internal API key for service auth")

    # Grid integration
    grid_operator_endpoint: str = Field(
        default="https://grid-operator.example.com/oadr",
        description="OpenADR / IEEE 2030.5 endpoint for the grid operator",
    )

    # MQTT
    mqtt_broker_url: str = Field(
        default="mqtt://localhost:1883",
        description="MQTT broker connection URL",
    )

    # Runtime behaviour
    debug: bool = Field(default=False, description="Enable FastAPI debug mode")
    log_level: str = Field(default="INFO", description="Python logging level")
    simulation_mode: bool = Field(
        default=False,
        description="Run without real hardware — generates synthetic data",
    )

    # CORS
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="List of origins allowed by CORS middleware",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton :class:`Settings` instance."""
    return Settings()
