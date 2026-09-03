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
