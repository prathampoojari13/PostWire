"""Configuration management for PostWire using Pydantic Settings."""

from typing import Literal
from pydantic import Field
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
    grafana_mcp_mode: Literal["mock", "live"] = Field(
        default="mock",
        description="Mode: 'mock' for local dev/testing; 'live' for real Grafana MCP server connection"
    )
    grafana_url: str = Field(default="http://localhost:3000", description="Grafana instance URL")
    grafana_service_account_token: str | None = Field(default=None, description="Grafana SA token")
    grafana_mcp_server_command: str = Field(
        default="npx -y @grafana/mcp-grafana",
        description="Command or path to launch official Grafana MCP server"
    )

    # API Server
    port: int = Field(default=8000, description="HTTP server port")
    host: str = Field(default="0.0.0.0", description="HTTP server host")


settings = Settings()
