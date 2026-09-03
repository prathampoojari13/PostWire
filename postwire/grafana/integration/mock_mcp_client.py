"""
Mock Grafana MCP Client.

STRICT USAGE NOTICE:
This mock adapter is ONLY for local development and deterministic automated tests.
It provides simulated Prometheus PromQL and Loki LogQL responses matching the active scenario.
In production/hackathon final deployment, POSTWIRE_GRAFANA_MODE=live must be used with the official Grafana MCP server.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from postwire.grafana.integration.interface import GrafanaMCPClientInterface
from postwire.telemetry.models import TelemetryPoint


class MockGrafanaMCPClient(GrafanaMCPClientInterface):
    """
    Simulates the official Grafana MCP tool responses for local development and testing.
    Can be dynamically bound to the current scenario's telemetry points.
    """

    def __init__(self, telemetry_points: Optional[List[TelemetryPoint]] = None):
        self._points = telemetry_points or []

    @property
    def mode(self) -> str:
        return "mock (local development & testing only)"

    def set_telemetry(self, points: List[TelemetryPoint]) -> None:
        """Update active telemetry context for simulated Prometheus/Loki responses."""
        self._points = points

    async def discover_tools(self) -> List[Dict[str, Any]]:
        """List simulated MCP tools available in mock mode."""
        return [
            {
                "name": "query_prometheus",
                "description": "Execute PromQL queries against Prometheus datasource",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "time_range": {"type": "string"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "query_loki",
                "description": "Execute LogQL queries against Loki datasource",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "list_alerts",
                "description": "Retrieve active Grafana alerting rules",
                "inputSchema": {"type": "object"}
            }
        ]

    async def query_prometheus(self, query: str, time_range: str = "5m") -> Dict[str, Any]:
        """
        Simulates PromQL query execution against streaming delivery metrics.
        Returns Grafana/Prometheus vector format.
        """
        now = datetime.now(timezone.utc).timestamp()
        results = []

        q_lower = query.lower()

        if "http_requests_total" in q_lower or "request_rate" in q_lower:
            total_rps = sum(p.request_rate_rps for p in self._points) if self._points else 180000.0
            results.append({
                "metric": {"__name__": "http_requests_total_rate", "tier": "edge_ingress"},
                "value": [now, str(round(total_rps, 2))]
            })

        elif "cache_hit_ratio" in q_lower or "cdn" in q_lower:
            avg_hit = (
                sum(p.cdn_cache_hit_ratio for p in self._points) / len(self._points)
                if self._points else 0.975
            )
            results.append({
                "metric": {"__name__": "cdn_cache_hit_ratio", "service": "edge_cdn"},
                "value": [now, str(round(avg_hit, 4))]
            })

        elif "drm" in q_lower or "license" in q_lower:
            regions_seen = set(p.region for p in self._points) if self._points else []
            for r in regions_seen:
                r_pts = [p for p in self._points if p.region == r]
                avg_drm = sum(p.drm_license_latency_ms for p in r_pts) / len(r_pts)
                results.append({
                    "metric": {"__name__": "drm_license_duration_ms", "region": r.value},
                    "value": [now, str(round(avg_drm, 1))]
                })
            if not results:
                results.append({
                    "metric": {"__name__": "drm_license_duration_ms", "region": "global"},
                    "value": [now, "32.5"]
                })

        elif "5xx" in q_lower or "error" in q_lower:
            for p in self._points:
                if p.http_5xx_rate > 0.01:
                    results.append({
                        "metric": {
                            "__name__": "http_5xx_rate",
                            "region": p.region.value,
                            "device": p.device_type.value
                        },
                        "value": [now, str(p.http_5xx_rate)]
                    })
            if not results:
                results.append({
                    "metric": {"__name__": "http_5xx_rate", "cluster": "all"},
                    "value": [now, "0.0003"]
                })

        else:
            results.append({
                "metric": {"query": query, "datasource": "mock_prometheus"},
                "value": [now, "1.0"]
            })

        return {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": results
            },
            "mcp_source": "mock_grafana_mcp"
        }

    async def query_loki(self, logql: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Simulates Loki log queries.
        Inspects whether any degraded slices exist and emits realistic log entries.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        logs = []

        has_drm_degradation = any(
            p.drm_license_latency_ms > 500.0 for p in self._points
        )

        logql_lower = logql.lower()

        if "drm" in logql_lower or "license" in logql_lower or "key" in logql_lower:
            if has_drm_degradation:
                logs.append({
                    "timestamp": now_iso,
                    "labels": {"app": "drm-key-service", "region": "apac-south", "level": "ERROR"},
                    "line": "[ERROR] PoolExhaustionException: Widevine/PlayReady upstream proxy timed out after 1500ms for client SmartTV-APAC"
                })
                logs.append({
                    "timestamp": now_iso,
                    "labels": {"app": "drm-key-service", "region": "apac-south", "level": "WARN"},
                    "line": "[WARN] HTTP 504 Gateway Timeout while contacting regional keystore cluster ap-south-1"
                })
            else:
                logs.append({
                    "timestamp": now_iso,
                    "labels": {"app": "drm-key-service", "region": "global", "level": "INFO"},
                    "line": "[INFO] DRM license issue rate healthy. 99th percentile latency: 34ms."
                })

        elif "edge" in logql_lower or "cdn" in logql_lower or "ingress" in logql_lower:
            logs.append({
                "timestamp": now_iso,
                "labels": {"app": "edge-proxy", "level": "INFO"},
                "line": "[INFO] Ingress load balancer capacity at 42%. CDN origin shield operational."
            })

        else:
            logs.append({
                "timestamp": now_iso,
                "labels": {"source": "mock_loki", "query": logql},
                "line": f"[INFO] Log stream evaluated for query '{logql}'. No critical anomalies reported."
            })

        return logs[:limit]

    async def list_active_alerts(self, filter_labels: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Simulates active Grafana alert rules."""
        alerts = []
        has_drm_spike = any(p.drm_license_latency_ms > 500.0 for p in self._points)
        has_traffic_spike = sum(p.request_rate_rps for p in self._points) > 500000.0 if self._points else False

        if has_traffic_spike:
            alerts.append({
                "alert_name": "EdgeIngressTrafficSpike",
                "state": "firing",
                "severity": "warning",
                "summary": "Ingress request rate exceeded 1M rps (>5x threshold)",
                "labels": {"tier": "edge_ingress"}
            })

        if has_drm_spike:
            alerts.append({
                "alert_name": "DRMLicenseLatencyHigh",
                "state": "firing",
                "severity": "critical",
                "summary": "p99 DRM key retrieval latency exceeded 1000ms in region apac-south",
                "labels": {"service": "drm-key-service", "region": "apac-south"}
            })

        return alerts
