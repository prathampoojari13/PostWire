"""FastAPI REST server for PostWire Incident Commander."""

from typing import Any, Dict, List, Literal, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from postwire.agent.commander import PostWireCommander
from postwire.config import settings
from postwire.qoe.viewer_analytics import ViewerQoEAnalytics
from postwire.telemetry.models import (
    AggregateTelemetry,
    IncidentReport,
    MovieReleaseContext,
    Region,
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

# Enable CORS for local development and UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

commander = PostWireCommander()
analytics = ViewerQoEAnalytics()


class ScenarioSummary(BaseModel):
    id: str
    name: str
    description: str
    release_title: str
    expected_classification: str


class RegionalQoEBreakdown(BaseModel):
    region: str
    concurrent_viewers: int
    viewer_impact_score: float
    playback_failure_rate: float
    rebuffer_ratio: float
    drm_license_latency_ms: float
    manifest_latency_ms: float
    status: Literal["HEALTHY", "WARNING", "CRITICAL"]


class InvestigationResponse(BaseModel):
    scenario_id: str
    alert_event: str
    release_context: MovieReleaseContext
    aggregate_qoe: AggregateTelemetry
    report: IncidentReport
    regional_breakdown: List[RegionalQoEBreakdown] = Field(default_factory=list)


class SimulationActionRequest(BaseModel):
    scenario_id: Optional[str] = "regional_streaming_incident"
    action_type: Optional[str] = "drm_failover"


class SimulationActionResponse(BaseModel):
    status: str = "SIMULATED"
    action: str
    executed: bool = False
    message: str = "No production infrastructure was modified."
    target_cluster: str
    projected_playback_failure_reduction: str
    projected_ttfb: str
    safety_check: str = "Passed. Zero blast radius on adjacent tenant clusters."


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


def compute_regional_breakdown(points: List[TelemetryPoint]) -> List[RegionalQoEBreakdown]:
    """Aggregates telemetry points by geographic region into UI-ready metrics."""
    breakdown: List[RegionalQoEBreakdown] = []
    for r in Region:
        reg_points = [p for p in points if p.region == r]
        if not reg_points:
            continue
        agg = analytics.aggregate(reg_points, region=r)
        if agg.viewer_impact_score >= 20.0 or agg.avg_playback_failure_rate >= 0.02 or agg.avg_drm_license_latency_ms >= 200.0:
            st = "CRITICAL"
        elif agg.viewer_impact_score >= 10.0 or agg.avg_playback_failure_rate >= 0.01:
            st = "WARNING"
        else:
            st = "HEALTHY"
        breakdown.append(
            RegionalQoEBreakdown(
                region=r.value,
                concurrent_viewers=agg.total_concurrent_viewers,
                viewer_impact_score=round(agg.viewer_impact_score, 1),
                playback_failure_rate=round(agg.avg_playback_failure_rate, 4),
                rebuffer_ratio=round(agg.avg_rebuffer_ratio, 4),
                drm_license_latency_ms=round(agg.avg_drm_license_latency_ms, 1),
                manifest_latency_ms=round(agg.avg_manifest_latency_ms, 1),
                status=st,
            )
        )
    return breakdown


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
    regional = compute_regional_breakdown(points)

    return InvestigationResponse(
        scenario_id=scenario_id,
        alert_event=alert,
        release_context=context,
        aggregate_qoe=agg,
        report=report,
        regional_breakdown=regional,
    )


@app.get("/api/scenarios/{scenario_id}/regional-breakdown", response_model=List[RegionalQoEBreakdown])
async def get_regional_breakdown(scenario_id: str) -> List[RegionalQoEBreakdown]:
    """Retrieve regional QoE metrics matrix for a scenario."""
    if scenario_id == "normal_movie_premiere":
        _, _, points = generate_premiere_surge_telemetry()
    elif scenario_id == "regional_streaming_incident":
        _, _, points = generate_regional_incident_telemetry()
    else:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return compute_regional_breakdown(points)


@app.post("/api/actions/simulate", response_model=SimulationActionResponse)
async def simulate_action(req: Optional[SimulationActionRequest] = None) -> SimulationActionResponse:
    """
    Simulate an operational mitigation without modifying production infrastructure.
    Explicitly labeled as [SIMULATED ACTION].
    """
    scen = req.scenario_id if req else "regional_streaming_incident"
    if scen == "normal_movie_premiere":
        return SimulationActionResponse(
            status="SIMULATED",
            action="[SIMULATED ACTION] Maintain edge capacity configuration for scheduled global premiere surge.",
            executed=False,
            message="No production infrastructure was modified. Simulation only.",
            target_cluster="[SIMULATED] edge-delivery-mesh",
            projected_playback_failure_reduction="Nominal (0.12% steady state)",
            projected_ttfb="45ms (normal)",
            safety_check="[SIMULATED] Passed. Zero blast radius on adjacent tenant clusters.",
        )

    return SimulationActionResponse(
        status="SIMULATED",
        action="[SIMULATED ACTION] Recommend rerouting APAC-South SmartTV DRM traffic to secondary regional DRM key service cluster.",
        executed=False,
        message="No production infrastructure was modified. Simulation only.",
        target_cluster="[SIMULATED] secondary-regional-hsm-cluster",
        projected_playback_failure_reduction="14.8% -> 0.42% in 90 seconds",
        projected_ttfb="61ms projected (vs current 1,850ms)",
        safety_check="[SIMULATED] Passed. Zero blast radius on adjacent tenant clusters.",
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
