"""
Live Gemini + Google ADK Investigation Verification Script.
Executes the autonomous investigation loop against real Grafana Cloud with live Gemini.
Fails explicitly if Gemini credentials are not configured (no silent fallback).
"""

import asyncio
import os
import sys
from postwire.agent.commander import PostWireCommander
from postwire.agent.runtime import GoogleADKCommanderRuntime
from postwire.config import settings
from postwire.grafana.integration.live_mcp_client import LiveGrafanaMCPClient
from postwire.telemetry.scenarios import generate_regional_incident_telemetry


async def run_live_gemini_verification():
    print("=" * 70)
    print("PostWire — Milestone 3A: Live Google Gemini + ADK Investigation Verification")
    print("=" * 70)

    # 1. Check Google Authentication / Credentials
    has_gemini_key = bool(settings.gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    has_adc = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

    print(f"[*] PostWire AI Mode:       {settings.postwire_ai_mode}")
    print(f"[*] Target Gemini Model:     {settings.gemini_model}")
    print(f"[*] Google Cloud Auth:      {'[CONFIGURED]' if (has_gemini_key or has_adc) else '[MISSING]'}")
    print(f"[*] Target Grafana URL:     {settings.grafana_url}")
    print(f"[*] Grafana MCP Mode:       {settings.postwire_grafana_mode}")
    print("-" * 70)

    if not (has_gemini_key or has_adc):
        print("\n" + "!" * 70)
        print("LIVE GEMINI VERIFICATION BLOCKED — credentials not configured")
        print("!" * 70)
        print("\nRequired Google Cloud Authentication:")
        print("Option A (Fastest for hackathon):")
        print("  Add your Google Gemini API key to .env:")
        print("  GEMINI_API_KEY=AIzaSy...")
        print("\nOption B (Google Cloud / Vertex AI Application Default Credentials):")
        print("  Set GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json")
        print("  or run 'gcloud auth application-default login'")
        print("=" * 70)
        return {
            "gemini_live_succeeded": False,
            "blocked_reason": "credentials_not_configured",
        }

    # 2. Initialize Real Live Grafana MCP Client
    print("[1/3] Initializing Live Grafana MCP Client connecting to Grafana Cloud...")
    try:
        mcp_client = LiveGrafanaMCPClient()
        print(f"    [+] Connected to Grafana MCP: {mcp_client.mode}")
    except Exception as exc:
        print(f"    [-] Failed to initialize live Grafana MCP client: {exc}")
        return {"gemini_live_succeeded": False, "error": str(exc)}

    # 3. Initialize Google ADK Runtime without deterministic fallback
    print(f"[2/3] Constructing Google ADK Agent with Gemini ({settings.gemini_model})...")
    runtime = GoogleADKCommanderRuntime(model_name=settings.gemini_model)
    commander = PostWireCommander(mcp_client=mcp_client, runtime=runtime)

    # 4. Generate Regional Streaming Incident Scenario
    alert, context, points = generate_regional_incident_telemetry()
    print(f"    [+] Alert Event: '{alert}'")
    print(f"    [+] Release: '{context.title}' ({context.release_id})")

    # 5. Execute Live Gemini Investigation
    print("[3/3] Executing live Gemini-powered investigation loop...")
    try:
        report = await commander.investigate_anomaly(
            alert_event=alert,
            release_context=context,
            telemetry_points=points,
        )

        if "Fallback to deterministic engine" in report.summary:
            print("\n" + "!" * 70)
            print("LIVE GEMINI INFERENCE FAILED — Agent fell back to deterministic engine:")
            print(f"Details: {report.summary}")
            print("!" * 70)
            return {
                "gemini_live_succeeded": False,
                "error": report.summary,
            }

        print("\n" + "=" * 70)
        print("LIVE GEMINI INVESTIGATION RESULT:")
        print("=" * 70)
        print(f"Runtime:                  google_adk")
        print(f"Model:                    {settings.gemini_model}")
        print(f"Final Classification:     {report.classification.value}")
        print(f"Confidence:               {report.confidence:.2f}")
        print(f"Affected Region:          {report.affected_region}")
        print(f"Affected Device:          {report.affected_device}")
        print(f"Viewer Impact Score:      {report.viewer_impact_score:.2f}")
        print(f"Summary:                  {report.summary}")
        print(f"Recommended Mitigation:   {report.recommended_mitigation}")
        print("-" * 70)
        print("Tools Selected Dynamically by Gemini:")
        for step in report.investigation_steps:
            print(f"  * Step {step.step_number}: Tool '{step.tool_used}' -> {step.query_summary}")
            print(f"    Evidence: {step.evidence_discovered[:100]}...")
        print("=" * 70)

        return {
            "gemini_live_succeeded": True,
            "report": report,
        }

    except Exception as exc:
        print(f"    [-] Live Gemini investigation failed: {exc}")
        return {
            "gemini_live_succeeded": False,
            "error": str(exc),
        }


if __name__ == "__main__":
    asyncio.run(run_live_gemini_verification())
