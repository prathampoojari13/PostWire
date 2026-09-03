"""Configuration management for PostWire using Pydantic Settings."""

import os
import shutil
from typing import Literal, Optional
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_default_mcp_command() -> str:
    """Returns 'mcp-grafana' if on PATH, otherwise 'python -m uv tool run mcp-grafana'."""
    if shutil.which("mcp-grafana"):
        return "mcp-grafana"
    return "python -m uv tool run mcp-grafana"


class Settings(BaseSettings):
    """Application settings with environment variable fallbacks."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General
    environment: str = Field(default="development", description="Runtime environment")
    log_level: str = Field(default="INFO", description="Log verbosity")

    # Google Cloud / Gemini AI
    gemini_api_key: str | None = Field(default=None, description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-2.5-flash", description="Configurable Gemini model version")

    # Grafana MCP Integration
    postwire_grafana_mode: Literal["mock", "live"] = Field(
        default="mock",
        description="Mode: 'mock' for local dev/testing; 'live' for real Grafana MCP server connection"
    )
    grafana_mcp_mode: Literal["mock", "live"] | None = Field(
        default=None,
        description="Alias for postwire_grafana_mode"
    )

    grafana_url: str = Field(default="http://localhost:3000", description="Grafana instance URL")
    grafana_service_account_token: str | None = Field(default=None, description="Grafana SA token (glsa_...)")
    grafana_mcp_command: str = Field(
        default_factory=get_default_mcp_command,
        description="Command to launch official Grafana MCP server"
    )

    # Optional datasource UIDs (auto-discovered via MCP if omitted)
    grafana_prometheus_uid: Optional[str] = Field(default=None, description="Prometheus datasource UID")
    grafana_loki_uid: Optional[str] = Field(default=None, description="Loki datasource UID")

    # Integration test flag
    postwire_run_grafana_integration: bool = Field(
        default=False,
        description="Set to true to run live integration tests against real Grafana instance"
    )

    # API Server
    port: int = Field(default=8000, description="HTTP server port")
    host: str = Field(default="0.0.0.0", description="HTTP server host")

    @model_validator(mode="after")
    def sync_mode(self) -> "Settings":
        """Synchronize POSTWIRE_GRAFANA_MODE and GRAFANA_MCP_MODE."""
        env_mode = os.getenv("POSTWIRE_GRAFANA_MODE") or os.getenv("GRAFANA_MCP_MODE")
        if env_mode in ("mock", "live"):
            self.postwire_grafana_mode = env_mode  # type: ignore

        if self.grafana_mcp_mode and not os.getenv("POSTWIRE_GRAFANA_MODE"):
            self.postwire_grafana_mode = self.grafana_mcp_mode

        return self


settings = Settings()
