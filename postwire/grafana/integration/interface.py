"""Abstract interface for Grafana MCP clients."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class GrafanaMCPClientInterface(ABC):
    """
    Formal interface for Grafana telemetry retrieval.
    Implementations must adhere strictly to Grafana MCP tool semantics.
    """

    @property
    @abstractmethod
    def mode(self) -> str:
        """Returns runtime mode string: 'mock' (dev/testing) or 'live' (official MCP server)."""
        pass

    @abstractmethod
    async def query_prometheus(self, query: str, time_range: str = "5m") -> Dict[str, Any]:
        """
        Executes a PromQL instant or range metric query via Grafana MCP.
        Returns standard Prometheus JSON format: {'status': 'success', 'data': {'resultType': 'vector', 'result': [...]}}
        """
        pass

    @abstractmethod
    async def query_loki(self, logql: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Queries application and edge access logs via Grafana Loki MCP.
        Returns parsed log records with timestamps, stream labels, and line text.
        """
        pass

    @abstractmethod
    async def list_active_alerts(self, filter_labels: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieves active Grafana Alerting rules and firing incidents.
        """
        pass
