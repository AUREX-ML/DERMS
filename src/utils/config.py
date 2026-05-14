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

    # VPP — site edge identity
    site_id: str = Field(default="site_A", description="Unique site identifier")

    # VPP — ThingsBoard cloud
    tb_rest_url: str = Field(
        default="https://thingsboard.example.com",
        description="ThingsBoard CE REST API base URL",
    )
    tb_username: str = Field(default="", description="ThingsBoard admin e-mail")
    tb_password: str = Field(default="", description="ThingsBoard admin password")
    tb_mqtt_host: str = Field(
        default="thingsboard.example.com",
        description="ThingsBoard MQTT broker hostname",
    )
    tb_mqtt_port: int = Field(default=8883, description="ThingsBoard MQTT TLS port")
    tb_device_token: str = Field(
        default="", description="Per-site device token for ThingsBoard MQTT auth"
    )

    # VPP — local Mosquitto broker
    local_mqtt_host: str = Field(
        default="localhost", description="Local Mosquitto broker hostname"
    )
    local_mqtt_port: int = Field(
        default=1883, description="Local Mosquitto broker port"
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton :class:`Settings` instance."""
    return Settings()
