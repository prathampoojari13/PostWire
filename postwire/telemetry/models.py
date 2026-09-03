"""Pydantic schemas for OTT streaming telemetry, viewer QoE, and incident reports."""

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Region(str, Enum):
    US_EAST = "us-east"
    US_WEST = "us-west"
    EU_CENTRAL = "eu-central"
    APAC_SOUTH = "apac-south"
    LATAM = "latam"


class DeviceType(str, Enum):
    SMART_TV = "SmartTV"
    MOBILE = "Mobile"
    WEB = "Web"
    GAME_CONSOLE = "GameConsole"
    STREAMING_STICK = "StreamingStick"


class TelemetryPoint(BaseModel):
    """A granular slice of OTT streaming telemetry at a specific point in time."""
    timestamp: datetime = Field(description="Sample timestamp")
    region: Region = Field(description="Geographic delivery region")
    device_type: DeviceType = Field(description="Client playback device")

    # Infrastructure & Edge Delivery Metrics
    concurrent_viewers: int = Field(ge=0, description="Active concurrent viewer sessions")
    request_rate_rps: float = Field(ge=0.0, description="Client request rate in requests per second")
    cdn_cache_hit_ratio: float = Field(ge=0.0, le=1.0, description="CDN cache hit ratio (0.0 to 1.0)")
    origin_request_rate_rps: float = Field(ge=0.0, description="Origin shield / packager requests per second")
    http_5xx_rate: float = Field(ge=0.0, le=1.0, description="Proportion of HTTP 5xx errors (0.0 to 1.0)")

    # Latency Metrics (milliseconds)
    manifest_latency_ms: float = Field(ge=0.0, description="HLS/DASH manifest fetch latency in ms")
    drm_license_latency_ms: float = Field(ge=0.0, description="Widevine/FairPlay/PlayReady DRM license fetch latency in ms")

    # Viewer Quality-of-Experience (QoE) Metrics
    video_start_time_ms: float = Field(ge=0.0, description="Video start time / join time in ms")
    rebuffer_ratio: float = Field(ge=0.0, le=1.0, description="Time spent rebuffering / total playback time (0.0 to 1.0)")
    exit_before_video_start: float = Field(ge=0.0, le=1.0, description="Proportion of viewers who abandon before 1st frame (0.0 to 1.0)")
    playback_failure_rate: float = Field(ge=0.0, le=1.0, description="Fatal playback error rate (0.0 to 1.0)")


class AggregateTelemetry(BaseModel):
    """Global or regional aggregate rollup of streaming telemetry."""
    timestamp: datetime
    total_concurrent_viewers: int
    total_request_rate_rps: float
    avg_cdn_cache_hit_ratio: float
    total_origin_request_rate_rps: float
    avg_http_5xx_rate: float
    avg_manifest_latency_ms: float
    avg_drm_license_latency_ms: float
    avg_video_start_time_ms: float
    avg_rebuffer_ratio: float
    avg_exit_before_video_start: float
    avg_playback_failure_rate: float
    viewer_impact_score: float = Field(
        ge=0.0,
        le=100.0,
        description="Composite score (0-100) where >20 indicates moderate and >40 indicates severe viewer degradation"
    )


class MovieReleaseContext(BaseModel):
    """Context regarding scheduled movie premiere or major release."""
    release_id: str = Field(description="Unique movie release identifier")
    title: str = Field(description="Title of the film")
    premiere_window_start: datetime = Field(description="Scheduled premiere time")
    marketing_tier: Literal["BLOCKBUSTER", "FEATURE", "CATALOG"] = Field(
        description="Release scale tier"
    )
    expected_viewer_surge_factor: float = Field(
        default=8.0,
        description="Expected traffic multiplier during the premiere window compared to baseline"
    )
    target_regions: List[Region] = Field(default_factory=lambda: list(Region))
    high_value_devices: List[DeviceType] = Field(default_factory=lambda: list(DeviceType))
    description: str = Field(description="Release event narrative context")


class IncidentClassification(str, Enum):
    EXPECTED_PREMIERE_SURGE = "EXPECTED_PREMIERE_SURGE"
    INVESTIGATE = "INVESTIGATE"
    CRITICAL_STREAMING_INCIDENT = "CRITICAL_STREAMING_INCIDENT"


class InvestigationStep(BaseModel):
    """Public non-CoT investigation step record."""
    step_number: int
    tool_used: str
    query_summary: str
    evidence_discovered: str


class IncidentReport(BaseModel):
    """Final autonomous incident assessment and recommendation."""
    incident_id: str
    release_id: str
    timestamp: datetime
    classification: IncidentClassification
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    summary: str
    evidence: List[str]
    root_cause_hypothesis: Optional[str] = None
    viewer_impact_summary: str
    recommended_mitigation: str = Field(
        description="Recommended operational mitigation. Explicitly designated as SIMULATED."
    )
    investigation_steps: List[InvestigationStep] = Field(
        default_factory=list,
        description="Chronological steps taken during the investigation loop"
    )
