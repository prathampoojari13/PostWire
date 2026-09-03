"""Tests for Grafana MCP clients (Mock adapter, Live stdio interface, and error handling)."""

import os
import pytest
from postwire.grafana.integration import get_grafana_mcp_client
from postwire.grafana.integration.live_mcp_client import LiveGrafanaMCPClient
from postwire.grafana.integration.mock_mcp_client import MockGrafanaMCPClient
from postwire.telemetry.scenarios import generate_regional_incident_telemetry


# ---------------------------------------------------------------------------
# Mock MCP Adapter Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mock_mcp_discover_tools():
    client = MockGrafanaMCPClient()
    tools = await client.discover_tools()
    assert len(tools) >= 3
    tool_names = [t["name"] for t in tools]
    assert "query_prometheus" in tool_names
    assert "query_loki" in tool_names
    assert "list_alerts" in tool_names


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


# ---------------------------------------------------------------------------
# Live MCP Client Configuration & Validation Tests
# ---------------------------------------------------------------------------

def test_live_mcp_client_missing_token_raises_error():
    """Missing token must raise a clear ValueError, not pretend or fail silently."""
    with pytest.raises(ValueError, match="GRAFANA_SERVICE_ACCOUNT_TOKEN is required"):
        LiveGrafanaMCPClient(grafana_url="https://example.grafana.net", token=None)


def test_live_mcp_client_missing_url_raises_error():
    """Missing URL must raise a clear ValueError."""
    with pytest.raises(ValueError, match="GRAFANA_URL is required"):
        LiveGrafanaMCPClient(grafana_url="", token="glsa_valid_token_sample")


def test_live_mcp_client_valid_initialization():
    """Live client initializes cleanly with valid URL and token."""
    client = LiveGrafanaMCPClient(
        grafana_url="https://postwire-demo.grafana.net",
        token="glsa_demo_token_12345",
        command="mcp-grafana"
    )
    assert "live" in client.mode.lower()
    assert "postwire-demo.grafana.net" in client.mode
    server_params = client._get_server_params()
    assert server_params.command == "mcp-grafana"
    assert server_params.env["GRAFANA_URL"] == "https://postwire-demo.grafana.net"
    assert server_params.env["GRAFANA_SERVICE_ACCOUNT_TOKEN"] == "glsa_demo_token_12345"


# ---------------------------------------------------------------------------
# Safe Error Handling & Formatting Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_live_mcp_executable_missing_handled_safely():
    """If mcp-grafana binary is missing from PATH, client returns structured error rather than crashing."""
    client = LiveGrafanaMCPClient(
        grafana_url="https://postwire-demo.grafana.net",
        token="glsa_demo_token_12345",
        command="non_existent_mcp_binary_xyz_123"
    )

    res = await client.query_prometheus("up")
    assert res["status"] == "error"
    assert res["error"] == "mcp_executable_missing"
    assert "not found" in res["message"].lower() or "cannot find" in res["message"].lower()

    logs = await client.query_loki('{app="test"}')
    assert len(logs) == 1
    assert logs[0].get("status") == "error"
    assert logs[0].get("error") == "mcp_executable_missing"


def test_live_mcp_result_parsing():
    """Test conversion of various MCP CallToolResult outputs into structured data."""
    client = LiveGrafanaMCPClient(
        grafana_url="https://postwire-demo.grafana.net",
        token="glsa_demo_token_12345"
    )

    class MockBlock:
        def __init__(self, text):
            self.text = text

    class MockResult:
        def __init__(self, blocks):
            self.content = blocks

    # Case 1: JSON payload
    res1 = client._parse_tool_result(MockResult([MockBlock('{"status": "success", "data": [1, 2, 3]}')]))
    assert res1 == {"status": "success", "data": [1, 2, 3]}

    # Case 2: Plain text payload
    res2 = client._parse_tool_result(MockResult([MockBlock('Non-JSON raw text line')]))
    assert res2 == {"text": "Non-JSON raw text line"}


def test_client_factory_defaults_to_mock_when_token_absent(monkeypatch):
    """If mode is live but token is absent, client factory safely falls back to Mock client."""
    monkeypatch.setattr("postwire.config.settings.postwire_grafana_mode", "live")
    monkeypatch.setattr("postwire.config.settings.grafana_service_account_token", None)

    client = get_grafana_mcp_client()
    assert isinstance(client, MockGrafanaMCPClient)
    assert "mock" in client.mode.lower()


# ---------------------------------------------------------------------------
# Live Integration Test (Guarded: runs only when explicitly requested)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.skipif(
    os.getenv("POSTWIRE_RUN_GRAFANA_INTEGRATION") != "true",
    reason="Requires active Grafana Cloud stack and POSTWIRE_RUN_GRAFANA_INTEGRATION=true"
)
async def test_live_grafana_cloud_mcp_integration():
    """
    Live end-to-end integration test executed against real Grafana Cloud.
    Requires:
      - POSTWIRE_RUN_GRAFANA_INTEGRATION=true
      - GRAFANA_URL
      - GRAFANA_SERVICE_ACCOUNT_TOKEN
      - mcp-grafana on PATH
    """
    client = LiveGrafanaMCPClient()
    tools = await client.discover_tools()
    assert len(tools) > 0, "Failed to discover tools from live mcp-grafana server"

    # Query Prometheus
    prom_res = await client.query_prometheus("up")
    assert prom_res.get("status") == "success"

    # Query Loki
    loki_res = await client.query_loki('{job=~".+"}', limit=5)
    assert isinstance(loki_res, list)
