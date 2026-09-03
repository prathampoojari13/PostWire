"""Viewer Quality-of-Experience (QoE) analytics engine."""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from postwire.telemetry.models import (
    AggregateTelemetry,
    DeviceType,
    Region,
    TelemetryPoint,
)


class ViewerQoEAnalytics:
    """Computes viewer QoE aggregates, dimensional slices, and the Viewer Impact Score (VIS)."""

    @staticmethod
    def calculate_viewer_impact_score(
        playback_failure_rate: float,
        exit_before_video_start: float,
        rebuffer_ratio: float,
        video_start_time_ms: float
    ) -> float:
        """
        Calculates a composite Viewer Impact Score (0.0 - 100.0).
        - 0.0 - 15.0: Healthy viewer experience.
        - 15.0 - 35.0: Moderate degradation / degraded UX.
        - > 35.0: Critical viewer impairment (fatal dropouts / playback blocks).
        """
        score = 0.0

        # Fatal Playback Failures (heaviest weight: 0.10 failure = 50 pts)
        score += min(60.0, playback_failure_rate * 500.0)

        # Exit Before Video Start (EBVS): 0.10 EBVS = 20 pts
        score += min(20.0, exit_before_video_start * 200.0)

        # Rebuffering ratio: 0.05 rebuffer = 15 pts
        score += min(15.0, rebuffer_ratio * 300.0)

        # Join time / VST latency over baseline (800ms)
        if video_start_time_ms > 1200.0:
            excess_vst = video_start_time_ms - 1200.0
            score += min(15.0, (excess_vst / 1000.0) * 5.0)

        return round(min(100.0, max(0.0, score)), 2)

    def aggregate(
        self,
        points: List[TelemetryPoint],
        region: Optional[Region] = None,
        device_type: Optional[DeviceType] = None
    ) -> AggregateTelemetry:
        """Computes rollup metrics for a given subset of telemetry points."""
        filtered = points
        if region:
            filtered = [p for p in filtered if p.region == region]
        if device_type:
            filtered = [p for p in filtered if p.device_type == device_type]

        if not filtered:
            return AggregateTelemetry(
                timestamp=datetime.now(timezone.utc),
                total_concurrent_viewers=0,
                total_request_rate_rps=0.0,
                avg_cdn_cache_hit_ratio=1.0,
                total_origin_request_rate_rps=0.0,
                avg_http_5xx_rate=0.0,
                avg_manifest_latency_ms=0.0,
                avg_drm_license_latency_ms=0.0,
                avg_video_start_time_ms=0.0,
                avg_rebuffer_ratio=0.0,
                avg_exit_before_video_start=0.0,
                avg_playback_failure_rate=0.0,
                viewer_impact_score=0.0,
            )

        total_viewers = sum(p.concurrent_viewers for p in filtered)
        total_requests = sum(p.request_rate_rps for p in filtered)
        total_origin = sum(p.origin_request_rate_rps for p in filtered)

        # Weighted averages where applicable, or arithmetic average
        avg_cache_hit = sum(p.cdn_cache_hit_ratio for p in filtered) / len(filtered)
        avg_5xx = sum(p.http_5xx_rate for p in filtered) / len(filtered)
        avg_manifest = sum(p.manifest_latency_ms for p in filtered) / len(filtered)
        avg_drm = sum(p.drm_license_latency_ms for p in filtered) / len(filtered)
        avg_vst = sum(p.video_start_time_ms for p in filtered) / len(filtered)
        avg_rebuffer = sum(p.rebuffer_ratio for p in filtered) / len(filtered)
        avg_ebvs = sum(p.exit_before_video_start for p in filtered) / len(filtered)
        avg_failure = sum(p.playback_failure_rate for p in filtered) / len(filtered)

        vis = self.calculate_viewer_impact_score(
            playback_failure_rate=avg_failure,
            exit_before_video_start=avg_ebvs,
            rebuffer_ratio=avg_rebuffer,
            video_start_time_ms=avg_vst,
        )

        return AggregateTelemetry(
            timestamp=filtered[0].timestamp,
            total_concurrent_viewers=total_viewers,
            total_request_rate_rps=round(total_requests, 2),
            avg_cdn_cache_hit_ratio=round(avg_cache_hit, 4),
            total_origin_request_rate_rps=round(total_origin, 2),
            avg_http_5xx_rate=round(avg_5xx, 5),
            avg_manifest_latency_ms=round(avg_manifest, 1),
            avg_drm_license_latency_ms=round(avg_drm, 1),
            avg_video_start_time_ms=round(avg_vst, 1),
            avg_rebuffer_ratio=round(avg_rebuffer, 4),
            avg_exit_before_video_start=round(avg_ebvs, 4),
            avg_playback_failure_rate=round(avg_failure, 4),
            viewer_impact_score=vis,
        )

    def find_anomalous_slices(
        self,
        points: List[TelemetryPoint],
        vis_threshold: float = 20.0
    ) -> List[Dict]:
        """Detects specific region/device segments that breach acceptable QoE thresholds."""
        anomalies = []
        for p in points:
            slice_vis = self.calculate_viewer_impact_score(
                playback_failure_rate=p.playback_failure_rate,
                exit_before_video_start=p.exit_before_video_start,
                rebuffer_ratio=p.rebuffer_ratio,
                video_start_time_ms=p.video_start_time_ms,
            )
            if slice_vis >= vis_threshold or p.playback_failure_rate > 0.03:
                anomalies.append({
                    "region": p.region.value,
                    "device_type": p.device_type.value,
                    "viewer_impact_score": slice_vis,
                    "playback_failure_rate": p.playback_failure_rate,
                    "drm_license_latency_ms": p.drm_license_latency_ms,
                    "manifest_latency_ms": p.manifest_latency_ms,
                    "video_start_time_ms": p.video_start_time_ms,
                    "affected_viewers": p.concurrent_viewers,
                })
        return anomalies
