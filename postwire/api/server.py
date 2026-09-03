"""FastAPI REST server for PostWire Incident Commander."""

from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from postwire.agent.commander import PostWireCommander
from postwire.config import settings
from postwire.qoe.viewer_analytics import ViewerQoEAnalytics
from postwire.telemetry.models import (
    AggregateTelemetry,
    IncidentReport,
    MovieReleaseContext,
    TelemetryPoint,
)
from postwire.telemetry.scenarios import (
    generate_premiere_surge_telemetry,
    generate_regional_incident_telemetry,
    get_premiere_surge_context,
    get_regional_incident_context,
)

app = FastAPI(
    title="PostWire — Autonomous Streaming Release Incident Commander",
    description="Autonomous incident commander correlating movie release context, viewer QoE, and Grafana MCP telemetry.",
    version="0.2.0",
)

commander = PostWireCommander()
analytics = ViewerQoEAnalytics()


class ScenarioSummary(BaseModel):
    id: str
    name: str
    description: str
    release_title: str
    expected_classification: str


class InvestigationResponse(BaseModel):
    scenario_id: str
    alert_event: str
    release_context: MovieReleaseContext
    aggregate_qoe: AggregateTelemetry
    report: IncidentReport


class MCPQueryRequest(BaseModel):
    query_type: str = "prometheus"  # "prometheus" or "loki"
    query: str
    time_range_or_limit: str = "5m"


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Service health and active integration statuses."""
    return {
        "status": "healthy",
        "service": "PostWire Incident Commander",
        "version": "0.2.0",
        "gemini_model": settings.gemini_model,
        "postwire_ai_mode": settings.postwire_ai_mode,
        "commander_ai_runtime": commander.runtime.runtime_name,
        "postwire_grafana_mode": settings.postwire_grafana_mode,
        "grafana_mcp_mode": settings.postwire_grafana_mode,
        "grafana_mcp_command": settings.grafana_mcp_command,
        "grafana_mcp_active_mode": commander.mcp_client.mode,
        "environment": settings.environment,
    }


@app.get("/api/mcp/tools")
async def list_mcp_tools() -> List[Dict[str, Any]]:
    """List tools discovered from the active Grafana MCP adapter."""
    return await commander.grafana_tools.discover_tools()


@app.post("/api/mcp/query")
async def query_mcp_raw(req: MCPQueryRequest) -> Any:
    """Directly query Prometheus or Loki through the active Grafana MCP client."""
    if req.query_type == "prometheus":
        return await commander.grafana_tools.query_grafana_metrics(req.query, req.time_range_or_limit)
    elif req.query_type == "loki":
        limit = int(req.time_range_or_limit) if req.time_range_or_limit.isdigit() else 50
        return await commander.grafana_tools.query_grafana_logs(req.query, limit=limit)
    else:
        raise HTTPException(status_code=400, detail="Invalid query_type. Use 'prometheus' or 'loki'.")


@app.get("/api/scenarios", response_model=List[ScenarioSummary])
async def list_scenarios() -> List[ScenarioSummary]:
    """List available deterministic demo scenarios."""
    return [
        ScenarioSummary(
            id="normal_movie_premiere",
            name="Normal Movie Premiere Surge",
            description="8x traffic surge during global day-and-date premiere. CDN cache and viewer QoE remain nominal.",
            release_title=get_premiere_surge_context().title,
            expected_classification="EXPECTED_PREMIERE_SURGE",
        ),
        ScenarioSummary(
            id="regional_streaming_incident",
            name="Regional Streaming Incident",
            description="Global traffic appears normal, but APAC SmartTV viewers suffer DRM license timeouts and 15% playback dropouts.",
            release_title=get_regional_incident_context().title,
            expected_classification="CRITICAL_STREAMING_INCIDENT",
        ),
    ]


@app.post("/api/scenarios/{scenario_id}/investigate", response_model=InvestigationResponse)
async def investigate_scenario(scenario_id: str) -> InvestigationResponse:
    """
    Trigger the Autonomous Commander investigation loop for a specified demo scenario.
    """
    if scenario_id == "normal_movie_premiere":
        alert, context, points = generate_premiere_surge_telemetry()
    elif scenario_id == "regional_streaming_incident":
        alert, context, points = generate_regional_incident_telemetry()
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario '{scenario_id}' not found. Available: ['normal_movie_premiere', 'regional_streaming_incident']"
        )

    # Execute Commander investigation
    report = await commander.investigate_anomaly(
        alert_event=alert,
        release_context=context,
        telemetry_points=points,
    )

    agg = analytics.aggregate(points)

    return InvestigationResponse(
        scenario_id=scenario_id,
        alert_event=alert,
        release_context=context,
        aggregate_qoe=agg,
        report=report,
    )


@app.get("/api/scenarios/{scenario_id}/telemetry", response_model=List[TelemetryPoint])
async def get_scenario_telemetry(scenario_id: str) -> List[TelemetryPoint]:
    """Retrieve raw multi-dimensional telemetry points for a scenario."""
    if scenario_id == "normal_movie_premiere":
        _, _, points = generate_premiere_surge_telemetry()
    elif scenario_id == "regional_streaming_incident":
        _, _, points = generate_regional_incident_telemetry()
    else:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return points
