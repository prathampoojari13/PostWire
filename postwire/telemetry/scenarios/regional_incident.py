"""Deterministic Scenario 2: Regional Streaming Incident (APAC SmartTV DRM bottleneck)."""

from datetime import datetime, timezone
from typing import List, Tuple
from postwire.telemetry.generator import TelemetryGenerator
from postwire.telemetry.models import (
    MovieReleaseContext,
    Region,
    DeviceType,
    TelemetryPoint,
)


def get_regional_incident_context() -> MovieReleaseContext:
    """Release context for mid-tier regional premiere."""
    return MovieReleaseContext(
        release_id="rel_neontokyo_2026",
        title="Neon Tokyo: Origins",
        premiere_window_start=datetime(2026, 9, 3, 12, 30, 0, tzinfo=timezone.utc),
        marketing_tier="FEATURE",
        expected_viewer_surge_factor=1.2,
        target_regions=[Region.APAC_SOUTH, Region.US_WEST],
        high_value_devices=[DeviceType.SMART_TV, DeviceType.MOBILE],
        description="Anime action premiere. High concentration of connected SmartTV viewers in APAC-South timezone.",
    )


def generate_regional_incident_telemetry(seed: int = 202) -> Tuple[str, MovieReleaseContext, List[TelemetryPoint]]:
    """Generates synthetic telemetry representing normal aggregate traffic but severe APAC SmartTV DRM failures."""
    gen = TelemetryGenerator(seed=seed)
    context = get_regional_incident_context()

    # Alert triggering the investigation
    alert_event = (
        "ALERT[REGIONAL_QOE_DEGRADATION]: SRE Alert Manager flagged an elevated playback failure rate (>5%) "
        "and client license timeouts in region apac-south."
    )

    # SmartTV slice in APAC-South is experiencing severe DRM license timeouts
    degraded_slices = {
        f"{Region.APAC_SOUTH.value}:{DeviceType.SMART_TV.value}": "drm_license_timeout"
    }

    points = gen.generate_snapshot(
        timestamp=context.premiere_window_start,
        global_multiplier=1.15,
        degraded_slices=degraded_slices,
    )

    return alert_event, context, points
