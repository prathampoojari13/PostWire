"""Tests for telemetry schemas, generator, and scenarios."""

from postwire.telemetry.generator import TelemetryGenerator
from postwire.telemetry.models import DeviceType, Region, TelemetryPoint
from postwire.telemetry.scenarios import (
    generate_premiere_surge_telemetry,
    generate_regional_incident_telemetry,
    get_premiere_surge_context,
    get_regional_incident_context,
)


def test_telemetry_point_validation():
    gen = TelemetryGenerator(seed=42)
    pts = gen.generate_snapshot()
    assert len(pts) == len(Region) * len(DeviceType)
    for p in pts:
        assert isinstance(p, TelemetryPoint)
        assert 0.0 <= p.cdn_cache_hit_ratio <= 1.0
        assert 0.0 <= p.http_5xx_rate <= 1.0
        assert p.concurrent_viewers > 0
        assert p.request_rate_rps > 0.0
        assert p.manifest_latency_ms > 0.0
        assert p.drm_license_latency_ms > 0.0


def test_premiere_surge_scenario():
    alert, context, points = generate_premiere_surge_telemetry()
    assert "ALERT" in alert
    assert context.expected_viewer_surge_factor == 8.0
    total_viewers = sum(p.concurrent_viewers for p in points)
    # 8x baseline viewers should exceed 600,000
    assert total_viewers > 600_000
    # No slice should have elevated failures in normal premiere
    for p in points:
        assert p.playback_failure_rate < 0.02


def test_regional_incident_scenario():
    alert, context, points = generate_regional_incident_telemetry()
    assert "ALERT" in alert
    assert context.release_id == "rel_neontokyo_2026"
    # Find degraded slice
    degraded = [
        p for p in points
        if p.region == Region.APAC_SOUTH and p.device_type == DeviceType.SMART_TV
    ]
    assert len(degraded) == 1
    assert degraded[0].drm_license_latency_ms > 1000.0
    assert degraded[0].playback_failure_rate > 0.10
