"""
Google ADK Compatible Toolset for PostWire Incident Commander.
Binds cinema release context, viewer QoE analytics, and real Grafana MCP tools.
"""

from typing import Any, Dict, List, Optional
from postwire.agent.tools.grafana_mcp_tools import GrafanaMCPTools
from postwire.agent.tools.qoe_tools import QoEInvestigationTools
from postwire.telemetry.models import InvestigationStep


class PostWireADKToolset:
    """
    Exposes specialized streaming investigation capabilities as Google ADK tools.
    Preserves existing Grafana MCP and QoE implementations.
    """

    def __init__(self, grafana_tools: GrafanaMCPTools, qoe_tools: QoEInvestigationTools):
        self.grafana_tools = grafana_tools
        self.qoe_tools = qoe_tools
        self.investigation_steps: List[InvestigationStep] = []
        self._step_counter = 0

    def _record_step(self, tool_name: str, query_summary: str, evidence: str) -> None:
        self._step_counter += 1
        self.investigation_steps.append(
            InvestigationStep(
                step_number=self._step_counter,
                tool_used=tool_name,
                query_summary=query_summary,
                evidence_discovered=evidence,
            )
        )

    async def get_release_context(self) -> Dict[str, Any]:
        """
        Inspect movie release context for the active premiere.
        Returns title, marketing tier, expected viewer surge factor, target regions, and high-value devices.
        """
        context = await self.qoe_tools.get_release_context()
        evidence = (
            f"Release: '{context.get('title')}' ({context.get('marketing_tier')}), "
            f"Expected surge factor: {context.get('expected_viewer_surge_factor')}x, "
            f"Target devices: {', '.join(context.get('high_value_devices', []))}"
        )
        self._record_step("get_release_context", f"Release context for {context.get('release_id')}", evidence)
        return context

    async def inspect_viewer_qoe(
        self,
        region: Optional[str] = None,
        device_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Inspect real-time viewer Quality of Experience (QoE) metrics and multi-dimensional slices.
        Returns Viewer Impact Score (VIS 0-100), playback failure rate, rebuffering, join time, and any anomalous slices.
        """
        agg = await self.qoe_tools.get_viewer_qoe_aggregate(region=region, device_type=device_type)
        anomalies = await self.qoe_tools.scan_anomalous_viewer_slices(vis_threshold=20.0)

        evidence = (
            f"Viewers: {agg.get('total_concurrent_viewers', 0):,}, "
            f"VIS: {agg.get('viewer_impact_score')}, "
            f"Failure Rate: {agg.get('avg_playback_failure_rate', 0.0)*100:.2f}%, "
            f"Anomalous Slices: {len(anomalies)}"
        )
        query_desc = f"QoE aggregate (region={region or 'all'}, device={device_type or 'all'})"
        self._record_step("inspect_viewer_qoe", query_desc, evidence)

        return {
            "aggregate_qoe": agg,
            "anomalous_slices": anomalies,
            "has_critical_qoe_degradation": len(anomalies) > 0 or agg.get("viewer_impact_score", 0.0) > 30.0,
        }

    async def query_grafana_prometheus(
        self,
        query: str,
        time_range: str = "5m",
    ) -> Dict[str, Any]:
        """
        Query infrastructure metrics from Grafana Cloud Prometheus via official Grafana MCP.
        Use for PromQL queries such as 'sum(rate(http_requests_total[5m]))', 'cdn_cache_hit_ratio', etc.
        """
        res = await self.grafana_tools.query_grafana_metrics(query=query, time_range=time_range)
        val = "OK"
        if isinstance(res, dict) and "data" in res and "result" in res["data"]:
            r = res["data"]["result"]
            if r and isinstance(r, list) and "value" in r[0]:
                val = str(r[0]["value"][1])
        evidence = f"PromQL query '{query}' returned value: {val} via official Grafana MCP"
        self._record_step("query_grafana_prometheus", f"PromQL: {query}", evidence)
        return res

    async def query_grafana_loki(
        self,
        logql_query: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Query system and edge access logs from Grafana Cloud Loki via official Grafana MCP.
        Use for LogQL queries such as '{app=\"drm-key-service\"} |= \"error\"' or '{tier=\"edge_ingress\"}'.
        """
        logs = await self.grafana_tools.query_grafana_logs(logql_query=logql_query, limit=limit)
        count = len(logs)
        first_line = logs[0].get("line", "") if logs and isinstance(logs[0], dict) else ""
        evidence = f"Loki LogQL query '{logql_query}' returned {count} log entries. Sample: {first_line[:90]}"
        self._record_step("query_grafana_loki", f"LogQL: {logql_query}", evidence)
        return logs

    async def list_grafana_alerts(self) -> List[Dict[str, Any]]:
        """
        Inspect active Grafana Cloud alerts and firing rules via official Grafana MCP.
        """
        alerts = await self.grafana_tools.list_grafana_alerts()
        count = len(alerts)
        evidence = f"Grafana Alerting returned {count} active alert groups."
        self._record_step("list_grafana_alerts", "Active alert rules query", evidence)
        return alerts

    def get_tool_callables(self) -> List[Any]:
        """Returns the list of ADK-compatible tool functions."""
        return [
            self.get_release_context,
            self.inspect_viewer_qoe,
            self.query_grafana_prometheus,
            self.query_grafana_loki,
            self.list_grafana_alerts,
        ]
