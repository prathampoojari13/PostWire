"""Grafana MCP integration package."""

import logging
from postwire.config import settings
from postwire.grafana.integration.interface import GrafanaMCPClientInterface
from postwire.grafana.integration.live_mcp_client import LiveGrafanaMCPClient
from postwire.grafana.integration.mock_mcp_client import MockGrafanaMCPClient

logger = logging.getLogger(__name__)


def get_grafana_mcp_client() -> GrafanaMCPClientInterface:
    """
    Factory creating appropriate client based on POSTWIRE_GRAFANA_MODE.
    Defaults safely to MockGrafanaMCPClient if credentials are absent.
    """
    mode = settings.postwire_grafana_mode

    if mode == "live":
        if settings.grafana_service_account_token:
            logger.info("Initializing LiveGrafanaMCPClient with official mcp-grafana server.")
            return LiveGrafanaMCPClient()
        else:
            logger.warning(
                "POSTWIRE_GRAFANA_MODE is set to 'live' but GRAFANA_SERVICE_ACCOUNT_TOKEN is missing. "
                "Defaulting safely to MockGrafanaMCPClient."
            )
            return MockGrafanaMCPClient()

    return MockGrafanaMCPClient()


__all__ = [
    "GrafanaMCPClientInterface",
    "LiveGrafanaMCPClient",
    "MockGrafanaMCPClient",
    "get_grafana_mcp_client",
]
