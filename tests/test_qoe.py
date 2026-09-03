"""Tests for viewer QoE analytics and impact scoring."""

from postwire.qoe.viewer_analytics import ViewerQoEAnalytics
from postwire.telemetry.scenarios import (
    generate_premiere_surge_telemetry,
    generate_regional_incident_telemetry,
)


def test_viewer_impact_score_healthy():
    analytics = ViewerQoEAnalytics()
    vis = analytics.calculate_viewer_impact_score(
        playback_failure_rate=0.0005,
        exit_before_video_start=0.005,
        rebuffer_ratio=0.002,
        video_start_time_ms=850.0,
    )
    assert vis < 10.0


def test_viewer_impact_score_critical():
    analytics = ViewerQoEAnalytics()
    vis = analytics.calculate_viewer_impact_score(
        playback_failure_rate=0.15,
        exit_before_video_start=0.10,
        rebuffer_ratio=0.03,
        video_start_time_ms=4500.0,
    )
    assert vis > 50.0


def test_find_anomalous_slices():
    analytics = ViewerQoEAnalytics()
    _, _, points = generate_regional_incident_telemetry()
    anomalies = analytics.find_anomalous_slices(points, vis_threshold=20.0)
    assert len(anomalies) == 1
    assert anomalies[0]["region"] == "apac-south"
    assert anomalies[0]["device_type"] == "SmartTV"
    assert anomalies[0]["playback_failure_rate"] > 0.10
