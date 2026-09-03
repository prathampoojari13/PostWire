"""Tests for the autonomous Commander agent investigation loop and Google ADK integration."""

import pytest
from postwire.agent.commander import PostWireCommander
from postwire.agent.runtime import (
    DeterministicCommanderRuntime,
    GoogleADKCommanderRuntime,
    get_agent_runtime,
)
from postwire.agent.tools.adk_tools import PostWireADKToolset
from postwire.agent.tools.grafana_mcp_tools import GrafanaMCPTools
from postwire.agent.tools.qoe_tools import QoEInvestigationTools
from postwire.grafana.integration.mock_mcp_client import MockGrafanaMCPClient
from postwire.qoe.viewer_analytics import ViewerQoEAnalytics
from postwire.telemetry.models import (
    IncidentClassification,
    IncidentDecision,
    IncidentReport,
)
from postwire.telemetry.scenarios import (
    generate_premiere_surge_telemetry,
    generate_regional_incident_telemetry,
    get_premiere_surge_context,
)


# ---------------------------------------------------------------------------
# Offline Deterministic Commander Scenario Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_commander_normal_premiere_surge():
    mcp_mock = MockGrafanaMCPClient()
    commander = PostWireCommander(mcp_client=mcp_mock, runtime=DeterministicCommanderRuntime())

    alert, context, points = generate_premiere_surge_telemetry()
    report = await commander.investigate_anomaly(
        alert_event=alert,
        release_context=context,
        telemetry_points=points,
    )

    assert report.classification == IncidentClassification.EXPECTED_PREMIERE_SURGE
    assert report.incident_classification == IncidentClassification.EXPECTED_PREMIERE_SURGE
    assert report.confidence >= 0.90
    assert "CyberDune 2" in report.summary or "traffic" in report.summary.lower()
    assert len(report.investigation_steps) >= 3
    for step in report.investigation_steps:
        assert step.step_number > 0
        assert step.tool_used != ""
        assert step.query_summary != ""
        assert step.evidence_discovered != ""
    assert "[SIMULATED]" in report.recommended_mitigation
    assert "[SIMULATED]" in report.recommended_action


@pytest.mark.asyncio
async def test_commander_regional_incident():
    mcp_mock = MockGrafanaMCPClient()
    commander = PostWireCommander(mcp_client=mcp_mock, runtime=DeterministicCommanderRuntime())

    alert, context, points = generate_regional_incident_telemetry()
    report = await commander.investigate_anomaly(
        alert_event=alert,
        release_context=context,
        telemetry_points=points,
    )

    assert report.classification == IncidentClassification.CRITICAL_STREAMING_INCIDENT
    assert report.confidence >= 0.90
    assert "apac-south" in report.summary.lower() or "smarttv" in report.summary.lower()
    assert report.root_cause_hypothesis is not None
    assert "DRM" in report.root_cause_hypothesis or "license" in report.root_cause_hypothesis.lower()
    assert "[SIMULATED]" in report.recommended_mitigation
    assert report.affected_region == "apac-south"
    assert report.affected_device == "SmartTV"
    assert report.viewer_impact_score > 30.0
    assert len(report.evidence) >= 2


# ---------------------------------------------------------------------------
# Google ADK Agent Construction & Tool Registration Tests
# ---------------------------------------------------------------------------

def test_adk_agent_initialization():
    """Verify Google ADK Agent can be constructed with configured Gemini model."""
    runtime = GoogleADKCommanderRuntime(model_name="gemini-2.5-flash")
    assert runtime.model_name == "gemini-2.5-flash"
    assert "Google ADK Agent" in runtime.runtime_name

    mcp_mock = MockGrafanaMCPClient()
    grafana_tools = GrafanaMCPTools(mcp_mock)
    context = get_premiere_surge_context()
    qoe_tools = QoEInvestigationTools(
        analytics=ViewerQoEAnalytics(),
        release_context=context,
        telemetry_points=[],
    )

    toolset = PostWireADKToolset(grafana_tools=grafana_tools, qoe_tools=qoe_tools)
    agent = runtime.build_adk_agent(toolset)

    assert agent.name == "postwire_incident_commander"
    assert agent.model == "gemini-2.5-flash"
    assert agent.output_schema is IncidentReport


def test_adk_tool_registration():
    """Verify all 5 required tools are registered on the ADK Agent."""
    runtime = GoogleADKCommanderRuntime()
    mcp_mock = MockGrafanaMCPClient()
    grafana_tools = GrafanaMCPTools(mcp_mock)
    context = get_premiere_surge_context()
    qoe_tools = QoEInvestigationTools(
        analytics=ViewerQoEAnalytics(),
        release_context=context,
        telemetry_points=[],
    )

    toolset = PostWireADKToolset(grafana_tools=grafana_tools, qoe_tools=qoe_tools)
    agent = runtime.build_adk_agent(toolset)

    tool_names = [getattr(t, "__name__", str(t)) for t in agent.tools]
    assert "get_release_context" in tool_names
    assert "inspect_viewer_qoe" in tool_names
    assert "query_grafana_prometheus" in tool_names
    assert "query_grafana_loki" in tool_names
    assert "list_grafana_alerts" in tool_names


@pytest.mark.asyncio
async def test_adk_toolset_dynamic_capability():
    """Verify toolset can be dynamically invoked and tracks investigation steps cleanly."""
    mcp_mock = MockGrafanaMCPClient()
    _, context, points = generate_regional_incident_telemetry()
    mcp_mock.set_telemetry(points)

    grafana_tools = GrafanaMCPTools(mcp_mock)
    qoe_tools = QoEInvestigationTools(
        analytics=ViewerQoEAnalytics(),
        release_context=context,
        telemetry_points=points,
    )
    toolset = PostWireADKToolset(grafana_tools=grafana_tools, qoe_tools=qoe_tools)

    # Agent dynamically calls release context
    ctx = await toolset.get_release_context()
    assert ctx["title"] == "Neon Tokyo: Origins"
    assert len(toolset.investigation_steps) == 1

    # Agent dynamically calls viewer QoE
    qoe = await toolset.inspect_viewer_qoe()
    assert qoe["has_critical_qoe_degradation"] is True
    assert len(toolset.investigation_steps) == 2

    # Agent dynamically calls Prometheus via Grafana MCP
    prom = await toolset.query_grafana_prometheus("sum(rate(http_requests_total[5m]))")
    assert prom["status"] == "success"
    assert len(toolset.investigation_steps) == 3

    # Verify no private chain-of-thought leaked
    for step in toolset.investigation_steps:
        assert step.step_number > 0
        assert step.tool_used in ["get_release_context", "inspect_viewer_qoe", "query_grafana_prometheus"]
        assert step.evidence_discovered != ""


def test_structured_output_schema_conformance():
    """Verify IncidentReport and IncidentDecision conform strictly to the required schema."""
    report = IncidentReport(
        incident_id="inc_test123",
        release_id="rel_cyberdune2_2026",
        timestamp=context_ts(),
        classification=IncidentClassification.EXPECTED_PREMIERE_SURGE,
        confidence=0.98,
        summary="Nominal launch demand.",
        evidence=["Traffic 8x matches premiere schedule."],
        recommended_mitigation="[SIMULATED] Maintain edge capacity.",
        affected_region=None,
        affected_device=None,
        viewer_impact_score=3.2,
    )

    assert isinstance(report, IncidentDecision)
    assert report.incident_classification == IncidentClassification.EXPECTED_PREMIERE_SURGE
    assert report.recommended_action == "[SIMULATED] Maintain edge capacity."
    assert "[SIMULATED]" in report.recommended_mitigation


def test_runtime_selection_mechanism(monkeypatch):
    """Verify POSTWIRE_AI_MODE selects appropriate runtime."""
    monkeypatch.setattr("postwire.config.settings.postwire_ai_mode", "offline")
    runtime_offline = get_agent_runtime()
    assert isinstance(runtime_offline, DeterministicCommanderRuntime)

    # When in google_adk mode and key is provided
    monkeypatch.setattr("postwire.config.settings.postwire_ai_mode", "google_adk")
    monkeypatch.setattr("postwire.config.settings.gemini_api_key", "mock_key")
    runtime_adk = get_agent_runtime()
    assert isinstance(runtime_adk, GoogleADKCommanderRuntime)


@pytest.mark.asyncio
async def test_all_adk_tool_responses_are_json_serializable():
    """
    Regression test: verify every PostWire ADK tool response is strictly JSON serializable.
    Ensures datetime objects (such as 'timestamp') are serialized to ISO-8601 strings
    and never cause TypeError in Google ADK serialization flows.
    """
    import json
    mcp_mock = MockGrafanaMCPClient()
    _, context, points = generate_regional_incident_telemetry()
    mcp_mock.set_telemetry(points)

    grafana_tools = GrafanaMCPTools(mcp_mock)
    qoe_tools = QoEInvestigationTools(
        analytics=ViewerQoEAnalytics(),
        release_context=context,
        telemetry_points=points,
    )
    toolset = PostWireADKToolset(grafana_tools=grafana_tools, qoe_tools=qoe_tools)

    # 1. get_release_context
    ctx = await toolset.get_release_context()
    dumped_ctx = json.dumps(ctx)
    assert isinstance(json.loads(dumped_ctx), dict)
    assert isinstance(ctx["premiere_window_start"], str)

    # 2. inspect_viewer_qoe (contains aggregate_qoe with 'timestamp')
    qoe = await toolset.inspect_viewer_qoe()
    dumped_qoe = json.dumps(qoe)
    loaded_qoe = json.loads(dumped_qoe)
    assert isinstance(loaded_qoe, dict)
    # Verify timestamp is serialized to ISO string, not a raw datetime object
    assert "timestamp" in qoe["aggregate_qoe"]
    assert isinstance(qoe["aggregate_qoe"]["timestamp"], str)
    assert "T" in qoe["aggregate_qoe"]["timestamp"] or len(qoe["aggregate_qoe"]["timestamp"]) >= 10

    # 3. query_grafana_prometheus
    prom = await toolset.query_grafana_prometheus("up")
    dumped_prom = json.dumps(prom)
    assert isinstance(json.loads(dumped_prom), dict)

    # 4. query_grafana_loki
    loki = await toolset.query_grafana_loki('{app="drm"}')
    dumped_loki = json.dumps(loki)
    assert isinstance(json.loads(dumped_loki), list)

    # 5. list_grafana_alerts
    alerts = await toolset.list_grafana_alerts()
    dumped_alerts = json.dumps(alerts)
    assert isinstance(json.loads(dumped_alerts), list)


@pytest.mark.asyncio
async def test_adk_quota_exhaustion_activates_deterministic_fallback(monkeypatch):
    """
    Verify that when Gemini returns an HTTP 429 / RESOURCE_EXHAUSTED daily quota error,
    PostWire cleanly activates the deterministic safety fallback without crashing or repeating retries.
    """
    runtime = GoogleADKCommanderRuntime(model_name="gemini-3.6-flash")
    mcp_mock = MockGrafanaMCPClient()
    alert, context, points = generate_regional_incident_telemetry()
    mcp_mock.set_telemetry(points)

    grafana_tools = GrafanaMCPTools(mcp_mock)
    qoe_tools = QoEInvestigationTools(
        analytics=ViewerQoEAnalytics(),
        release_context=context,
        telemetry_points=points,
    )

    # Mock runner.run_async to raise 429 RESOURCE_EXHAUSTED (simulating daily quota exhaustion)
    async def mock_run_async(*args, **kwargs):
        raise Exception(
            "429 ResourceExhausted: Quota exceeded for metric: GenerateRequestsPerDayPerProjectPerModel, quotaValue: 20"
        )
        yield  # make it an async generator

    from google.adk import Runner
    monkeypatch.setattr(Runner, "run_async", mock_run_async)

    report = await runtime.investigate(alert, grafana_tools, qoe_tools)

    # Verify fallback executed and generated a valid, safe incident report
    assert report.classification == IncidentClassification.CRITICAL_STREAMING_INCIDENT
    assert "Gemini quota exhausted — deterministic safety fallback activated." in report.summary
    assert "[SIMULATED]" in report.recommended_mitigation
    assert len(report.investigation_steps) >= 3


def context_ts():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)
