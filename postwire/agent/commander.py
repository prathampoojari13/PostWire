"""Autonomous PostWire Incident Commander Agent."""

import logging
from typing import List, Optional
from postwire.agent.runtime import AgentRuntimeInterface, get_agent_runtime
from postwire.agent.tools.grafana_mcp_tools import GrafanaMCPTools
from postwire.agent.tools.qoe_tools import QoEInvestigationTools
from postwire.grafana.integration import (
    GrafanaMCPClientInterface,
    MockGrafanaMCPClient,
    get_grafana_mcp_client,
)
from postwire.qoe.viewer_analytics import ViewerQoEAnalytics
from postwire.telemetry.models import (
    IncidentReport,
    MovieReleaseContext,
    TelemetryPoint,
)

logger = logging.getLogger(__name__)


class PostWireCommander:
    """
    Autonomous Streaming Release Incident Commander.
    Operates with specialized investigation tools to correlate movie release context,
    viewer QoE, and Grafana infrastructure telemetry.
    """

    def __init__(
        self,
        mcp_client: Optional[GrafanaMCPClientInterface] = None,
        runtime: Optional[AgentRuntimeInterface] = None,
        analytics: Optional[ViewerQoEAnalytics] = None,
    ):
        self.mcp_client = mcp_client or get_grafana_mcp_client()
        self.runtime = runtime or get_agent_runtime()
        self.analytics = analytics or ViewerQoEAnalytics()
        self.grafana_tools = GrafanaMCPTools(self.mcp_client)

    async def investigate_anomaly(
        self,
        alert_event: str,
        release_context: MovieReleaseContext,
        telemetry_points: List[TelemetryPoint],
    ) -> IncidentReport:
        """
        Executes the autonomous investigation loop:
        ALERT -> release context -> hypothesis -> Grafana MCP tools -> QoE tools -> correlation -> classification -> mitigation.
        """
        logger.info("Commander activated by alert: %s", alert_event)
        logger.info("Release context: %s (%s)", release_context.title, release_context.marketing_tier)
        logger.info("Commander AI runtime: %s", self.runtime.runtime_name)
        logger.info("Grafana MCP runtime mode: %s", self.mcp_client.mode)

        # If mock client is in use for local dev, synchronize its simulated telemetry with the current dataset
        if isinstance(self.mcp_client, MockGrafanaMCPClient):
            self.mcp_client.set_telemetry(telemetry_points)

        qoe_tools = QoEInvestigationTools(
            analytics=self.analytics,
            release_context=release_context,
            telemetry_points=telemetry_points,
        )

        report = await self.runtime.investigate(
            alert=alert_event,
            grafana_tools=self.grafana_tools,
            qoe_tools=qoe_tools,
        )

        logger.info(
            "Investigation concluded for release %s. Classification: %s (Confidence: %.2f)",
            release_context.release_id,
            report.classification.value,
            report.confidence,
        )
        return report
