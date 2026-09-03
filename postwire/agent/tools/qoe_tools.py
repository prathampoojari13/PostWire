"""Viewer Quality-of-Experience and Release Context investigation tools."""

from typing import Any, Dict, List, Optional
from postwire.qoe.viewer_analytics import ViewerQoEAnalytics
from postwire.telemetry.models import (
    DeviceType,
    MovieReleaseContext,
    Region,
    TelemetryPoint,
)


class QoEInvestigationTools:
    """Specialized investigation tools for viewer telemetry and cinema release context."""

    def __init__(
        self,
        analytics: ViewerQoEAnalytics,
        release_context: MovieReleaseContext,
        telemetry_points: List[TelemetryPoint]
    ):
        self.analytics = analytics
        self.release_context = release_context
        self.points = telemetry_points

    def set_context(
        self,
        release_context: MovieReleaseContext,
        telemetry_points: List[TelemetryPoint]
    ) -> None:
        """Update current operational context."""
        self.release_context = release_context
        self.points = telemetry_points

    async def get_release_context(self) -> Dict[str, Any]:
        """
        Inspect movie release context (premiere window, expected surge multiplier, target devices).
        """
        return {
            "release_id": self.release_context.release_id,
            "title": self.release_context.title,
            "premiere_window_start": self.release_context.premiere_window_start.isoformat(),
            "marketing_tier": self.release_context.marketing_tier,
            "expected_viewer_surge_factor": self.release_context.expected_viewer_surge_factor,
            "high_value_devices": [d.value for d in self.release_context.high_value_devices],
            "description": self.release_context.description,
        }

    async def get_viewer_qoe_aggregate(
        self,
        region: Optional[str] = None,
        device_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve aggregate viewer QoE metrics (Viewer Impact Score, failure rates, rebuffering, join time).
        Optionally filter by region (e.g. 'apac-south') or device_type (e.g. 'SmartTV').
        """
        reg_enum = Region(region) if region else None
        dev_enum = DeviceType(device_type) if device_type else None

        agg = self.analytics.aggregate(
            self.points,
            region=reg_enum,
            device_type=dev_enum
        )
        return agg.model_dump()

    async def scan_anomalous_viewer_slices(
        self,
        vis_threshold: float = 20.0
    ) -> List[Dict[str, Any]]:
        """
        Scan all multidimensional slices (region x device) to pinpoint viewer experience degradation.
        Finds localized dropouts hidden inside overall healthy traffic.
        """
        return self.analytics.find_anomalous_slices(
            self.points,
            vis_threshold=vis_threshold
        )
