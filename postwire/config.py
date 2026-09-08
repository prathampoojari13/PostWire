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
    google_api_key: str | None = Field(default=None, description="Google API key alternative")
    gemini_model: str = Field(default="gemini-3.6-flash", description="Configurable Gemini model version")
    google_cloud_project: str | None = Field(default=None, description="Google Cloud Project ID for Vertex AI ADC")
    google_cloud_location: str = Field(default="us-central1", description="Google Cloud region for Vertex AI")
    google_genai_use_vertexai: bool = Field(default=False, description="Set to true to use Google Cloud Vertex AI ADC")

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

    # AI Engine Mode
    postwire_ai_mode: Literal["google_adk", "offline"] = Field(
        default="offline",
        description="AI mode: 'google_adk' for real Google ADK + Gemini; 'offline' for deterministic test engine"
    )

    @model_validator(mode="after")
    def sync_mode(self) -> "Settings":
        """Synchronize mode flags with environment variables."""
        env_mode = os.getenv("POSTWIRE_GRAFANA_MODE") or os.getenv("GRAFANA_MCP_MODE")
        if env_mode in ("mock", "live"):
            self.postwire_grafana_mode = env_mode  # type: ignore

        if self.grafana_mcp_mode and not os.getenv("POSTWIRE_GRAFANA_MODE"):
            self.postwire_grafana_mode = self.grafana_mcp_mode

        ai_env = os.getenv("POSTWIRE_AI_MODE")
        has_ai_creds = bool(
            self.gemini_api_key
            or self.google_api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        )
        if ai_env in ("google_adk", "offline"):
            self.postwire_ai_mode = ai_env  # type: ignore
        elif has_ai_creds and ai_env != "offline":
            self.postwire_ai_mode = "google_adk"

        return self


settings = Settings()
