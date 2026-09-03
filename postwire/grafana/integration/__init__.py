"""Grafana MCP integration package."""

from postwire.config import settings
from postwire.grafana.integration.interface import GrafanaMCPClientInterface
from postwire.grafana.integration.live_mcp_client import LiveGrafanaMCPClient
from postwire.grafana.integration.mock_mcp_client import MockGrafanaMCPClient


def get_grafana_mcp_client() -> GrafanaMCPClientInterface:
    """Factory creating appropriate client based on GRAFANA_MCP_MODE."""
    if settings.grafana_mcp_mode == "live":
        return LiveGrafanaMCPClient()
    return MockGrafanaMCPClient()


__all__ = [
    "GrafanaMCPClientInterface",
    "LiveGrafanaMCPClient",
    "MockGrafanaMCPClient",
    "get_grafana_mcp_client",
]
