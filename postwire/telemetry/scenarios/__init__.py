"""Scenario definitions for PostWire demos."""

from postwire.telemetry.scenarios.premiere_surge import (
    generate_premiere_surge_telemetry,
    get_premiere_surge_context,
)
from postwire.telemetry.scenarios.regional_incident import (
    generate_regional_incident_telemetry,
    get_regional_incident_context,
)

__all__ = [
    "generate_premiere_surge_telemetry",
    "get_premiere_surge_context",
    "generate_regional_incident_telemetry",
    "get_regional_incident_context",
]
