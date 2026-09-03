"""Grafana MCP investigation tools for the PostWire Commander Agent."""

from typing import Any, Dict, List, Optional
from postwire.grafana.integration import GrafanaMCPClientInterface


class GrafanaMCPTools:
    """Specialized investigation tools that interact directly with Grafana via MCP."""

    def __init__(self, mcp_client: GrafanaMCPClientInterface):
        self.client = mcp_client

    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover tools exposed by the configured Grafana MCP server."""
        return await self.client.discover_tools()

    async def query_grafana_metrics(self, query: str, time_range: str = "5m") -> Dict[str, Any]:
        """
        Query infrastructure metrics from Prometheus/Grafana using PromQL over MCP.
        Examples:
        - sum(rate(http_requests_total[5m]))
        - cdn_cache_hit_ratio
        - rate(drm_license_errors_total[5m])
        """
        return await self.client.query_prometheus(query=query, time_range=time_range)

    async def query_grafana_logs(self, logql_query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Query system and edge access logs from Loki/Grafana using LogQL over MCP.
        Examples:
        - {app="drm-key-service"} |= "error"
        - {tier="edge_ingress"} |= "504"
        """
        return await self.client.query_loki(logql=logql_query, limit=limit)

    async def list_grafana_alerts(self) -> List[Dict[str, Any]]:
        """List active Grafana alerts and firing rules over MCP."""
        return await self.client.list_active_alerts()
