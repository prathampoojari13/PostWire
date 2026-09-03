"""Tests for the autonomous Commander agent investigation loop."""

import pytest
from postwire.agent.commander import PostWireCommander
from postwire.grafana.integration.mock_mcp_client import MockGrafanaMCPClient
from postwire.telemetry.models import IncidentClassification
from postwire.telemetry.scenarios import (
    generate_premiere_surge_telemetry,
    generate_regional_incident_telemetry,
)


@pytest.mark.asyncio
async def test_commander_normal_premiere_surge():
    mcp_mock = MockGrafanaMCPClient()
    commander = PostWireCommander(mcp_client=mcp_mock)

    alert, context, points = generate_premiere_surge_telemetry()
    report = await commander.investigate_anomaly(
        alert_event=alert,
        release_context=context,
        telemetry_points=points,
    )

    # Asserts
    assert report.classification == IncidentClassification.EXPECTED_PREMIERE_SURGE
    assert report.confidence >= 0.90
    assert "CyberDune 2" in report.summary or "traffic" in report.summary.lower()
    assert len(report.investigation_steps) >= 3
    # Verify non-CoT format
    for step in report.investigation_steps:
        assert step.step_number > 0
        assert step.tool_used != ""
        assert step.query_summary != ""
        assert step.evidence_discovered != ""
    assert "[SIMULATED]" in report.recommended_mitigation


@pytest.mark.asyncio
async def test_commander_regional_incident():
    mcp_mock = MockGrafanaMCPClient()
    commander = PostWireCommander(mcp_client=mcp_mock)

    alert, context, points = generate_regional_incident_telemetry()
    report = await commander.investigate_anomaly(
        alert_event=alert,
        release_context=context,
        telemetry_points=points,
    )

    # Asserts
    assert report.classification == IncidentClassification.CRITICAL_STREAMING_INCIDENT
    assert report.confidence >= 0.90
    assert "apac-south" in report.summary.lower() or "smarttv" in report.summary.lower()
    assert report.root_cause_hypothesis is not None
    assert "DRM" in report.root_cause_hypothesis or "license" in report.root_cause_hypothesis.lower()
    assert "[SIMULATED]" in report.recommended_mitigation
    assert len(report.evidence) >= 2
