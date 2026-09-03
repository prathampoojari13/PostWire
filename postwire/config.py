"""Configuration management for PostWire using Pydantic Settings."""

import os
from typing import Literal
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    # POSTWIRE_GRAFANA_MODE supports "mock" (dev/tests) and "live" (official mcp-grafana server)
    postwire_grafana_mode: Literal["mock", "live"] = Field(
        default="mock",
        description="Mode: 'mock' for local dev/testing; 'live' for real Grafana MCP server connection"
    )
    # Backwards-compatibility alias for GRAFANA_MCP_MODE
    grafana_mcp_mode: Literal["mock", "live"] | None = Field(
        default=None,
        description="Alias for postwire_grafana_mode"
    )

    grafana_url: str = Field(default="http://localhost:3000", description="Grafana instance URL")
    grafana_service_account_token: str | None = Field(default=None, description="Grafana SA token (glsa_...)")
    grafana_mcp_command: str = Field(
        default="mcp-grafana",
        description="Command or binary to launch official Grafana MCP server (e.g. 'mcp-grafana' or 'uvx mcp-grafana')"
    )

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
        """Synchronize POSTWIRE_GRAFANA_MODE and GRAFANA_MCP_MODE, and default to mock if credentials missing."""
        # Support either environment variable name
        env_mode = os.getenv("POSTWIRE_GRAFANA_MODE") or os.getenv("GRAFANA_MCP_MODE")
        if env_mode in ("mock", "live"):
            self.postwire_grafana_mode = env_mode  # type: ignore

        if self.grafana_mcp_mode and not os.getenv("POSTWIRE_GRAFANA_MODE"):
            self.postwire_grafana_mode = self.grafana_mcp_mode

        # If live mode requested but token is missing, log/default safely to mock unless running integration tests
        if self.postwire_grafana_mode == "live" and not self.grafana_service_account_token:
            # Keep as live so LiveGrafanaMCPClient can report explicit configuration requirement
            pass

        return self


settings = Settings()
