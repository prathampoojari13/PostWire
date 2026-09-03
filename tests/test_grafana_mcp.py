"""Tests for Grafana MCP clients (Mock adapter and Live interface)."""

import pytest
from postwire.grafana.integration.live_mcp_client import LiveGrafanaMCPClient
from postwire.grafana.integration.mock_mcp_client import MockGrafanaMCPClient
from postwire.telemetry.scenarios import generate_regional_incident_telemetry


@pytest.mark.asyncio
async def test_mock_mcp_prometheus_query():
    client = MockGrafanaMCPClient()
    _, _, points = generate_regional_incident_telemetry()
    client.set_telemetry(points)

    res = await client.query_prometheus("sum(rate(http_requests_total[5m]))")
    assert res["status"] == "success"
    assert len(res["data"]["result"]) > 0
    val = float(res["data"]["result"][0]["value"][1])
    assert val > 10000.0


@pytest.mark.asyncio
async def test_mock_mcp_loki_log_query():
    client = MockGrafanaMCPClient()
    _, _, points = generate_regional_incident_telemetry()
    client.set_telemetry(points)

    logs = await client.query_loki('{app="drm-key-service"} |= "error"')
    assert len(logs) > 0
    assert any("drm" in log["labels"]["app"] for log in logs)


def test_live_mcp_client_validation():
    # Attempting to use Live client without token must raise an explicit ValueError, not fake success
    with pytest.raises(ValueError, match="GRAFANA_SERVICE_ACCOUNT_TOKEN is required"):
        LiveGrafanaMCPClient(token=None)
