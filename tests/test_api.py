"""Tests for the PostWire FastAPI endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from postwire.api.server import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "gemini_model" in data
    assert "grafana_mcp_mode" in data
    assert "postwire_grafana_mode" in data
    assert "grafana_mcp_command" in data


@pytest.mark.asyncio
async def test_list_scenarios_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    assert len(scenarios) == 2
    ids = [s["id"] for s in scenarios]
    assert "normal_movie_premiere" in ids
    assert "regional_streaming_incident" in ids


@pytest.mark.asyncio
async def test_investigate_scenario_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/scenarios/normal_movie_premiere/investigate")
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == "normal_movie_premiere"
    assert data["report"]["classification"] == "EXPECTED_PREMIERE_SURGE"
    assert "[SIMULATED]" in data["report"]["recommended_mitigation"]


@pytest.mark.asyncio
async def test_mcp_tools_discovery_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/mcp/tools")
    assert response.status_code == 200
    tools = response.json()
    assert isinstance(tools, list)
    assert len(tools) >= 3


@pytest.mark.asyncio
async def test_mcp_raw_query_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/mcp/query", json={
            "query_type": "prometheus",
            "query": "sum(rate(http_requests_total[5m]))",
            "time_range_or_limit": "5m"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_cors_headers():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            }
        )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") in ["http://localhost:5173", "*"]


@pytest.mark.asyncio
async def test_regional_breakdown_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Test regional incident scenario
        res = await ac.get("/api/scenarios/regional_streaming_incident/regional-breakdown")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 3
        # Check apac-south is identified as CRITICAL in this scenario
        apac = next((r for r in data if r["region"] == "apac-south"), None)
        assert apac is not None
        assert apac["status"] == "CRITICAL"
        assert apac["playback_failure_rate"] > 0.02
        assert apac["drm_license_latency_ms"] > 200.0

        # Test normal premiere surge scenario (all healthy)
        res_normal = await ac.get("/api/scenarios/normal_movie_premiere/regional-breakdown")
        assert res_normal.status_code == 200
        normal_data = res_normal.json()
        for reg in normal_data:
            assert reg["status"] == "HEALTHY"


@pytest.mark.asyncio
async def test_investigate_includes_regional_breakdown():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/scenarios/regional_streaming_incident/investigate")
        assert res.status_code == 200
        data = res.json()
        assert "regional_breakdown" in data
        assert len(data["regional_breakdown"]) >= 3


@pytest.mark.asyncio
async def test_simulation_action_endpoint_never_claims_execution():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/api/actions/simulate", json={
            "scenario_id": "regional_streaming_incident",
            "action_type": "drm_failover"
        })
        assert res.status_code == 200
        data = res.json()
        # Safety assertions
        assert data["status"] == "SIMULATED"
        assert data["executed"] is False
        assert "[SIMULATED ACTION]" in data["action"]
        assert "No production infrastructure was modified" in data["message"]
        assert "[SIMULATED]" in data["target_cluster"]
