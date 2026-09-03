"""Synthetic OTT streaming telemetry generator with realistic metric relationships."""

from datetime import datetime, timezone
import random
from typing import Dict, List, Optional
from postwire.telemetry.models import DeviceType, Region, TelemetryPoint


class TelemetryGenerator:
    """Generates synthetic multi-dimensional streaming telemetry matching OTT delivery characteristics."""

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    def generate_point(
        self,
        timestamp: datetime,
        region: Region,
        device_type: DeviceType,
        viewer_multiplier: float = 1.0,
        degraded: bool = False,
        degradation_type: Optional[str] = None
    ) -> TelemetryPoint:
        """Generate a single metric point for a region and device slice."""
        # Regional baseline weight
        region_weights = {
            Region.US_EAST: 0.35,
            Region.US_WEST: 0.25,
            Region.EU_CENTRAL: 0.20,
            Region.APAC_SOUTH: 0.12,
            Region.LATAM: 0.08,
        }

        # Device baseline weight
        device_weights = {
            DeviceType.SMART_TV: 0.45,
            DeviceType.MOBILE: 0.25,
            DeviceType.WEB: 0.15,
            DeviceType.STREAMING_STICK: 0.10,
            DeviceType.GAME_CONSOLE: 0.05,
        }

        # Baseline baseline: ~100,000 global concurrent viewers
        base_viewers = int(100_000 * region_weights[region] * device_weights[device_type] * viewer_multiplier)
        # Small deterministic jitter (+/- 2%)
        jitter = 1.0 + (self._rng.uniform(-0.02, 0.02))
        concurrent_viewers = max(10, int(base_viewers * jitter))

        # Request rate: approx 1.8 requests/sec per viewer (manifests + video segments)
        request_rate_rps = round(concurrent_viewers * 1.8 * self._rng.uniform(0.98, 1.02), 2)

        # CDN cache hit ratio: normally 96.5% - 98.5%
        cdn_cache_hit_ratio = round(self._rng.uniform(0.965, 0.982), 4)

        # Origin request rate = total requests * (1 - cache_hit_ratio)
        origin_request_rate_rps = round(request_rate_rps * (1.0 - cdn_cache_hit_ratio), 2)

        # Normal baselines
        http_5xx_rate = round(self._rng.uniform(0.0001, 0.0006), 5)
        manifest_latency_ms = round(self._rng.uniform(18.0, 32.0), 1)
        drm_license_latency_ms = round(self._rng.uniform(28.0, 45.0), 1)
        video_start_time_ms = round(self._rng.uniform(750.0, 950.0), 1)
        rebuffer_ratio = round(self._rng.uniform(0.001, 0.003), 4)
        exit_before_video_start = round(self._rng.uniform(0.004, 0.008), 4)
        playback_failure_rate = round(self._rng.uniform(0.0002, 0.0008), 4)

        # Apply specific degradations if triggered for this slice
        if degraded:
            if degradation_type == "drm_license_timeout":
                # Severe DRM bottleneck: license server connection pool exhaustion
                drm_license_latency_ms = round(self._rng.uniform(1400.0, 2200.0), 1)
                manifest_latency_ms = round(manifest_latency_ms * 1.8, 1)
                http_5xx_rate = round(self._rng.uniform(0.08, 0.18), 4)
                video_start_time_ms = round(self._rng.uniform(3200.0, 5800.0), 1)
                exit_before_video_start = round(self._rng.uniform(0.075, 0.125), 4)
                playback_failure_rate = round(self._rng.uniform(0.12, 0.18), 4)
                rebuffer_ratio = round(self._rng.uniform(0.005, 0.012), 4)

            elif degradation_type == "cdn_origin_shield_collapse":
                cdn_cache_hit_ratio = round(self._rng.uniform(0.65, 0.78), 4)
                origin_request_rate_rps = round(request_rate_rps * (1.0 - cdn_cache_hit_ratio), 2)
                manifest_latency_ms = round(self._rng.uniform(350.0, 850.0), 1)
                http_5xx_rate = round(self._rng.uniform(0.04, 0.09), 4)
                rebuffer_ratio = round(self._rng.uniform(0.045, 0.095), 4)
                playback_failure_rate = round(self._rng.uniform(0.03, 0.07), 4)

        return TelemetryPoint(
            timestamp=timestamp,
            region=region,
            device_type=device_type,
            concurrent_viewers=concurrent_viewers,
            request_rate_rps=request_rate_rps,
            cdn_cache_hit_ratio=cdn_cache_hit_ratio,
            origin_request_rate_rps=origin_request_rate_rps,
            http_5xx_rate=http_5xx_rate,
            manifest_latency_ms=manifest_latency_ms,
            drm_license_latency_ms=drm_license_latency_ms,
            video_start_time_ms=video_start_time_ms,
            rebuffer_ratio=rebuffer_ratio,
            exit_before_video_start=exit_before_video_start,
            playback_failure_rate=playback_failure_rate,
        )

    def generate_snapshot(
        self,
        timestamp: Optional[datetime] = None,
        global_multiplier: float = 1.0,
        degraded_slices: Optional[Dict[str, str]] = None
    ) -> List[TelemetryPoint]:
        """Generate a complete matrix across all regions and device types."""
        ts = timestamp or datetime.now(timezone.utc)
        degraded_slices = degraded_slices or {}

        points: List[TelemetryPoint] = []
        for region in Region:
            for device in DeviceType:
                slice_key = f"{region.value}:{device.value}"
                is_degraded = slice_key in degraded_slices
                deg_type = degraded_slices.get(slice_key)

                point = self.generate_point(
                    timestamp=ts,
                    region=region,
                    device_type=device,
                    viewer_multiplier=global_multiplier,
                    degraded=is_degraded,
                    degradation_type=deg_type,
                )
                points.append(point)

        return points
