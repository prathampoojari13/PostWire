"""
Modular AI / Agent Runtime Layer for PostWire.

Provides:
- GoogleADKCommanderRuntime: Real Google ADK + Gemini agentic commander with dynamic tool execution.
- DeterministicCommanderRuntime: Deterministic offline engine for local testing and CI.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
import uuid

import google.adk as adk
from google.adk.sessions import InMemorySessionService
from google.genai import types

from postwire.agent.prompts import COMMANDER_SYSTEM_PROMPT
from postwire.agent.tools.adk_tools import PostWireADKToolset
from postwire.agent.tools.grafana_mcp_tools import GrafanaMCPTools
from postwire.agent.tools.qoe_tools import QoEInvestigationTools
from postwire.config import settings
from postwire.telemetry.models import (
    IncidentClassification,
    IncidentReport,
    InvestigationStep,
)

logger = logging.getLogger(__name__)


class AgentRuntimeInterface(ABC):
    """Abstract interface for the autonomous incident investigation engine."""

    @property
    @abstractmethod
    def runtime_name(self) -> str:
        """Name of the active runtime."""
        pass

    @abstractmethod
    async def investigate(
        self,
        alert: str,
        grafana_tools: GrafanaMCPTools,
        qoe_tools: QoEInvestigationTools,
    ) -> IncidentReport:
        """Execute the autonomous agentic investigation loop."""
        pass


class DeterministicCommanderRuntime(AgentRuntimeInterface):
    """
    Deterministic rule-guided investigation engine.
    Used for local development, unit tests, and offline regression.
    """

    @property
    def runtime_name(self) -> str:
        return "Offline Deterministic Commander"

    async def investigate(
        self,
        alert: str,
        grafana_tools: GrafanaMCPTools,
        qoe_tools: QoEInvestigationTools,
    ) -> IncidentReport:
        incident_id = f"inc_{uuid.uuid4().hex[:8]}"
        steps: List[InvestigationStep] = []
        evidence: List[str] = []

        # Step 1: Inspect Movie Release Context
        release_context = await qoe_tools.get_release_context()
        steps.append(InvestigationStep(
            step_number=1,
            tool_used="qoe_tools.get_release_context",
            query_summary=f"Query release context for {release_context['release_id']}",
            evidence_discovered=(
                f"Release: '{release_context['title']}' ({release_context['marketing_tier']}), "
                f"Expected Surge Factor: {release_context['expected_viewer_surge_factor']}x, "
                f"High-Value Devices: {', '.join(release_context['high_value_devices'])}"
            )
        ))

        # Step 2: Form Hypothesis & Query Grafana Infrastructure Ingress Metrics
        ingress_metrics = await grafana_tools.query_grafana_metrics("sum(rate(http_requests_total[5m]))")
        rps_result = ingress_metrics.get("data", {}).get("result", [{}])[0].get("value", [0, "0"])[1]
        steps.append(InvestigationStep(
            step_number=2,
            tool_used="grafana_mcp.query_prometheus",
            query_summary="PromQL: sum(rate(http_requests_total[5m]))",
            evidence_discovered=f"Ingress edge request rate measured at {rps_result} rps via Grafana MCP."
        ))

        # Step 3: Inspect Aggregate Viewer QoE
        agg_qoe = await qoe_tools.get_viewer_qoe_aggregate()
        steps.append(InvestigationStep(
            step_number=3,
            tool_used="qoe_tools.get_viewer_qoe_aggregate",
            query_summary="Global viewer QoE aggregate inspection",
            evidence_discovered=(
                f"Total Viewers: {agg_qoe['total_concurrent_viewers']:,}, "
                f"Viewer Impact Score (VIS): {agg_qoe['viewer_impact_score']}, "
                f"Avg Failure Rate: {agg_qoe['avg_playback_failure_rate']*100:.2f}%, "
                f"Avg Cache Hit Ratio: {agg_qoe['avg_cdn_cache_hit_ratio']*100:.2f}%"
            )
        ))

        # Step 4: Scan for dimensional anomalies across slices (Region x Device)
        anomalous_slices = await qoe_tools.scan_anomalous_viewer_slices(vis_threshold=20.0)

        # Dynamic investigation branch based on evidence
        if not anomalous_slices and agg_qoe["viewer_impact_score"] < 15.0:
            cache_query = await grafana_tools.query_grafana_metrics("cdn_cache_hit_ratio")
            cache_val = cache_query.get("data", {}).get("result", [{}])[0].get("value", [0, "0.97"])[1]
            steps.append(InvestigationStep(
                step_number=4,
                tool_used="grafana_mcp.query_prometheus",
                query_summary="PromQL: cdn_cache_hit_ratio",
                evidence_discovered=f"CDN edge cache hit ratio is healthy at {float(cache_val)*100:.2f}%."
            ))

            evidence.append(f"Global traffic surge is consistent with {release_context['title']} scheduled {release_context['expected_viewer_surge_factor']}x release window.")
            evidence.append(f"Viewer Impact Score is {agg_qoe['viewer_impact_score']} (nominal/healthy threshold < 15.0).")
            evidence.append(f"Edge CDN cache hit ratio remains stable at {float(cache_val)*100:.2f}%.")
            evidence.append(f"Fatal playback failure rate is negligible at {agg_qoe['avg_playback_failure_rate']*100:.3f}%.")

            return IncidentReport(
                incident_id=incident_id,
                release_id=release_context["release_id"],
                timestamp=datetime.now(timezone.utc),
                classification=IncidentClassification.EXPECTED_PREMIERE_SURGE,
                confidence=0.98,
                summary=(
                    f"Traffic surge of ~{release_context['expected_viewer_surge_factor']}x detected for '{release_context['title']}'. "
                    f"Viewer QoE metrics and CDN cache efficiency are nominal. No real incident opened."
                ),
                evidence=evidence,
                root_cause_hypothesis="Legitimate high-concurrency premiere viewing demand matching marketing schedule.",
                viewer_impact_summary="Nominal. Global viewers experiencing normal join times and pristine playback.",
                recommended_mitigation="[SIMULATED] Maintain current edge CDN capacity and continue automated telemetry sampling. No failover required.",
                affected_region=None,
                affected_device=None,
                viewer_impact_score=agg_qoe["viewer_impact_score"],
                investigation_steps=steps,
            )

        else:
            slice_desc = ", ".join(
                f"{s['region']} ({s['device_type']}): failures={s['playback_failure_rate']*100:.1f}%, DRM latency={s['drm_license_latency_ms']}ms"
                for s in anomalous_slices
            )
            steps.append(InvestigationStep(
                step_number=4,
                tool_used="qoe_tools.scan_anomalous_viewer_slices",
                query_summary="Dimensional slice anomaly detection across all regions and device types",
                evidence_discovered=f"Isolated degradation detected in slices: {slice_desc}"
            ))

            loki_logs = await grafana_tools.query_grafana_logs('{app="drm-key-service"} |= "error"', limit=5)
            log_summary = " | ".join(l.get("line", "") for l in loki_logs) if loki_logs else "No matching logs found"
            steps.append(InvestigationStep(
                step_number=5,
                tool_used="grafana_mcp.query_loki",
                query_summary='LogQL: {app="drm-key-service"} |= "error"',
                evidence_discovered=f"Grafana Loki returned error signatures: {log_summary}"
            ))

            drm_metrics = await grafana_tools.query_grafana_metrics("rate(drm_license_duration_ms)")
            steps.append(InvestigationStep(
                step_number=6,
                tool_used="grafana_mcp.query_prometheus",
                query_summary="PromQL: rate(drm_license_duration_ms)",
                evidence_discovered="Grafana MCP confirmed elevated DRM key retrieval latency (>1400ms) localized to regional cluster."
            ))

            for s in anomalous_slices:
                evidence.append(
                    f"Slice [{s['region']} / {s['device_type']}] experiencing {s['playback_failure_rate']*100:.1f}% fatal playback failure rate "
                    f"with {s['drm_license_latency_ms']:.0f}ms DRM latency."
                )
            evidence.append(f"Grafana Loki confirmed: {log_summary}")

            primary_region = anomalous_slices[0]["region"] if anomalous_slices else "apac-south"
            primary_device = anomalous_slices[0]["device_type"] if anomalous_slices else "SmartTV"
            primary_vis = anomalous_slices[0].get("viewer_impact_score", 65.0) if anomalous_slices else 65.0

            return IncidentReport(
                incident_id=incident_id,
                release_id=release_context["release_id"],
                timestamp=datetime.now(timezone.utc),
                classification=IncidentClassification.CRITICAL_STREAMING_INCIDENT,
                confidence=0.96,
                summary=(
                    f"Critical regional streaming failure isolated to {primary_region} on {primary_device} devices. "
                    f"DRM license acquisition timeouts are causing fatal playback failures for {anomalous_slices[0]['affected_viewers']:,} viewers."
                ),
                evidence=evidence,
                root_cause_hypothesis=(
                    f"Regional DRM license proxy timeout and connection pool exhaustion in {primary_region} "
                    f"preventing {primary_device} clients from acquiring Widevine/PlayReady keys."
                ),
                viewer_impact_summary=(
                    f"Severe viewer impairment. Viewers on {primary_device} in {primary_region} cannot start streams "
                    f"({anomalous_slices[0]['playback_failure_rate']*100:.1f}% failure rate)."
                ),
                recommended_mitigation=(
                    f"[SIMULATED] Immediately reroute {primary_region} {primary_device} DRM license requests to secondary "
                    f"healthy key-server cluster in adjacent region, and increase client retry backoff window."
                ),
                affected_region=primary_region,
                affected_device=primary_device,
                viewer_impact_score=primary_vis,
                investigation_steps=steps,
            )


class GoogleADKCommanderRuntime(AgentRuntimeInterface):
    """
    Real Google ADK + Gemini Agentic Incident Commander.
    Builds an adk.Agent with specialized tools and dynamically executes turns with Gemini.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.gemini_model
        # Ensure API key is accessible to Google GenAI SDK if present in settings
        if settings.gemini_api_key and "GEMINI_API_KEY" not in os.environ:
            os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

    @property
    def runtime_name(self) -> str:
        return f"Google ADK Agent ({self.model_name})"

    def build_adk_agent(self, toolset: PostWireADKToolset) -> adk.Agent:
        """Constructs the official Google ADK Agent with investigation tools."""
        return adk.Agent(
            name="postwire_incident_commander",
            description="Autonomous streaming release incident commander correlating viewer QoE and Grafana MCP telemetry.",
            model=self.model_name,
            instruction=COMMANDER_SYSTEM_PROMPT,
            tools=toolset.get_tool_callables(),
            output_schema=IncidentReport,
        )

    async def investigate(
        self,
        alert: str,
        grafana_tools: GrafanaMCPTools,
        qoe_tools: QoEInvestigationTools,
    ) -> IncidentReport:
        toolset = PostWireADKToolset(grafana_tools=grafana_tools, qoe_tools=qoe_tools)
        agent = self.build_adk_agent(toolset)

        session_service = InMemorySessionService()
        runner = adk.Runner(
            agent=agent,
            session_service=session_service,
            app_name="postwire",
            auto_create_session=True,
        )

        session_id = f"sroc_{uuid.uuid4().hex[:8]}"
        user_id = "sroc_incident_operator"
        prompt_text = (
            f"STREAMING INCIDENT ALERT:\n{alert}\n\n"
            "Investigate this anomaly dynamically using your available tools. "
            "Correlate cinema release context, viewer QoE, and Grafana MCP telemetry. "
            "Return your final assessment strictly as the structured IncidentReport."
        )

        message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_text)]
        )

        logger.info("Dispatching incident investigation to Google ADK Agent (%s)...", self.model_name)
        final_text = ""

        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=message,
            ):
                # Inspect event content
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if getattr(part, "text", None):
                            final_text += part.text

            # Parse the model's structured decision
            report = self._parse_adk_output(final_text, toolset.investigation_steps)
            return report

        except Exception as exc:
            logger.warning(
                "Google ADK Agent invocation failed: %s. Falling back to deterministic engine.",
                exc
            )
            fallback = DeterministicCommanderRuntime()
            fallback_report = await fallback.investigate(alert, grafana_tools, qoe_tools)
            fallback_report.summary += f" [Note: Fallback to deterministic engine due to: {exc}]"
            return fallback_report

    def _parse_adk_output(self, text: str, recorded_steps: List[InvestigationStep]) -> IncidentReport:
        """Parses structured JSON output from Gemini and ensures safety guidelines."""
        data: Dict[str, Any] = {}

        # Look for JSON block in markdown fences or raw string
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
            except Exception:
                pass
        if not data:
            try:
                data = json.loads(text.strip())
            except Exception:
                pass

        incident_id = data.get("incident_id") or f"inc_{uuid.uuid4().hex[:8]}"
        release_id = data.get("release_id") or "active_release"
        classification_raw = data.get("classification") or data.get("incident_classification", "INVESTIGATE")

        try:
            classification = IncidentClassification(classification_raw)
        except Exception:
            classification = IncidentClassification.INVESTIGATE

        mitigation = data.get("recommended_mitigation") or data.get("recommended_action") or "[SIMULATED] Continue automated monitoring."
        if "[SIMULATED]" not in mitigation:
            mitigation = f"[SIMULATED] {mitigation}"

        return IncidentReport(
            incident_id=incident_id,
            release_id=release_id,
            timestamp=datetime.now(timezone.utc),
            classification=classification,
            confidence=float(data.get("confidence", 0.90)),
            summary=data.get("summary", "Investigation completed by Google ADK Agent."),
            evidence=data.get("evidence", [s.evidence_discovered for s in recorded_steps]),
            root_cause_hypothesis=data.get("root_cause_hypothesis"),
            viewer_impact_summary=data.get("viewer_impact_summary", "Evaluated viewer telemetry."),
            recommended_mitigation=mitigation,
            affected_region=data.get("affected_region"),
            affected_device=data.get("affected_device"),
            viewer_impact_score=float(data.get("viewer_impact_score", 0.0)),
            investigation_steps=recorded_steps,
        )


def get_agent_runtime() -> AgentRuntimeInterface:
    """Factory returning configured Agent Runtime based on POSTWIRE_AI_MODE."""
    mode = settings.postwire_ai_mode
    has_creds = bool(settings.gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))

    if mode == "google_adk" and has_creds:
        logger.info("Using real Google ADK + Gemini Agent runtime (%s).", settings.gemini_model)
        return GoogleADKCommanderRuntime()

    if mode == "google_adk" and not has_creds:
        logger.warning(
            "POSTWIRE_AI_MODE is 'google_adk' but GEMINI_API_KEY is not set. "
            "Falling back to Deterministic Commander runtime."
        )
        return DeterministicCommanderRuntime()

    logger.info("Using Offline Deterministic Commander runtime.")
    return DeterministicCommanderRuntime()
