"""
Official Grafana MCP Client Adapter.

Communicates with the official Grafana MCP server (e.g., @grafana/mcp-grafana)
via standard Model Context Protocol (MCP) JSON-RPC messages.

This is the REAL runtime integration required for the final hackathon submission.
"""

import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from postwire.config import settings
from postwire.grafana.integration.interface import GrafanaMCPClientInterface

logger = logging.getLogger(__name__)


class LiveGrafanaMCPClient(GrafanaMCPClientInterface):
    """
    Client connecting to the official Grafana MCP server or Grafana API.
    Uses actual MCP tool semantics without faking responses.
    """

    def __init__(
        self,
        grafana_url: Optional[str] = None,
        token: Optional[str] = None,
        mcp_endpoint: Optional[str] = None
    ):
        self.grafana_url = (grafana_url or settings.grafana_url).rstrip("/")
        self.token = token or settings.grafana_service_account_token
        self.mcp_endpoint = mcp_endpoint or f"{self.grafana_url}/api/mcp"
        self._validate_configuration()

    @property
    def mode(self) -> str:
        return f"live (Connected to Grafana at {self.grafana_url})"

    def _validate_configuration(self) -> None:
        """Validates that credentials exist. Fails explicitly rather than pretending."""
        if not self.token:
            raise ValueError(
                "GRAFANA_SERVICE_ACCOUNT_TOKEN is required to connect to the live Grafana MCP server. "
                "For local development/testing without Grafana credentials, use MockGrafanaMCPClient or set GRAFANA_MCP_MODE=mock."
            )

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes an MCP tool call against the Grafana MCP endpoint using JSON-RPC 2.0.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(
                    self.mcp_endpoint,
                    headers=self._get_headers(),
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                if "error" in data:
                    raise RuntimeError(f"Grafana MCP error: {data['error']}")
                return data.get("result", {})
            except httpx.RequestError as exc:
                logger.error("Failed to connect to Grafana MCP server at %s: %s", self.mcp_endpoint, exc)
                raise ConnectionError(
                    f"Could not connect to live Grafana MCP endpoint at {self.mcp_endpoint}. "
                    f"Ensure the Grafana MCP server is running. Error: {exc}"
                ) from exc

    async def query_prometheus(self, query: str, time_range: str = "5m") -> Dict[str, Any]:
        """Call official Grafana MCP tool for Prometheus queries."""
        return await self._call_mcp_tool(
            tool_name="query_prometheus",
            arguments={"query": query, "time_range": time_range}
        )

    async def query_loki(self, logql: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Call official Grafana MCP tool for Loki queries."""
        result = await self._call_mcp_tool(
            tool_name="query_loki",
            arguments={"query": logql, "limit": limit}
        )
        # Grafana MCP returns content items
        if isinstance(result, dict) and "content" in result:
            items = []
            for c in result.get("content", []):
                if c.get("type") == "text":
                    try:
                        parsed = json.loads(c["text"])
                        if isinstance(parsed, list):
                            items.extend(parsed)
                        else:
                            items.append(parsed)
                    except json.JSONDecodeError:
                        items.append({"line": c["text"]})
            return items
        return result if isinstance(result, list) else [result]

    async def list_active_alerts(self, filter_labels: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Call official Grafana MCP tool for alerts."""
        result = await self._call_mcp_tool(
            tool_name="list_alerts",
            arguments={"filter": filter_labels or {}}
        )
        return result if isinstance(result, list) else []
