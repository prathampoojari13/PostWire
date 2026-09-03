"""Deterministic Scenario 1: Normal Movie Premiere Surge (8x Traffic Spike)."""

from datetime import datetime, timezone
from typing import List, Tuple
from postwire.telemetry.generator import TelemetryGenerator
from postwire.telemetry.models import (
    MovieReleaseContext,
    Region,
    DeviceType,
    TelemetryPoint,
)


def get_premiere_surge_context() -> MovieReleaseContext:
    """Release context for global blockbuster premiere."""
    return MovieReleaseContext(
        release_id="rel_cyberdune2_2026",
        title="CyberDune 2: Galactic Reckoning",
        premiere_window_start=datetime(2026, 9, 3, 12, 0, 0, tzinfo=timezone.utc),
        marketing_tier="BLOCKBUSTER",
        expected_viewer_surge_factor=8.0,
        target_regions=list(Region),
        high_value_devices=[DeviceType.SMART_TV, DeviceType.STREAMING_STICK],
        description="Global day-and-date premiere. Massive advertising campaign across TV and social media. Global traffic expected to jump 8x at premiere launch.",
    )


def generate_premiere_surge_telemetry(seed: int = 101) -> Tuple[str, MovieReleaseContext, List[TelemetryPoint]]:
    """Generates synthetic telemetry representing an 8x surge with healthy infrastructure and QoE."""
    gen = TelemetryGenerator(seed=seed)
    context = get_premiere_surge_context()

    # Alert triggering the investigation
    alert_event = (
        "ALERT[TRAFFIC_ANOMALY_TRIGGERED]: Global ingress request rate jumped from 180,000 rps to 1,440,000 rps (7.98x baseline). "
        "Threshold exceeded on edge ingress gateway."
    )

    # 8.0x traffic multiplier, no degraded slices
    points = gen.generate_snapshot(
        timestamp=context.premiere_window_start,
        global_multiplier=8.0,
        degraded_slices=None,
    )

    return alert_event, context, points
