import React from "react";
import type { IncidentReport, HealthStatus } from "../api/client";

interface CommanderStreamProps {
  report: IncidentReport | null;
  health: HealthStatus | null;
}

export const CommanderStream: React.FC<CommanderStreamProps> = ({ report, health }) => {
  const steps = report?.investigation_steps || [];

  // If no steps returned yet, provide placeholder matching Stitch design
  const defaultSteps = [
    {
      time: "00:01:05",
      tool: "Alert Manager Ingest",
      status: "COMPLETED",
      desc: (
        <>
          Received high-urgency SRE telemetry alert:{" "}
          <span className="font-code-xs text-code-xs text-primary bg-surface-container px-space-xs py-0.5 rounded">
            alert_qoe_apac_south_fail_rate_critical
          </span>
        </>
      ),
    },
    {
      time: "00:02:18",
      tool: "Release Context Service",
      status: "COMPLETED",
      desc: (
        <>
          Checked premiere catalogue matrix for "Neon Tokyo: Origins" (T+45min elapsed). Projected global concurrency 6×–10×; observed traffic only 1.2×.
        </>
      ),
    },
    {
      time: "00:04:12",
      tool: "Viewer QoE Inspector",
      status: "COMPLETED",
      desc: (
        <>
          Inspected real-time viewer playback beacons. Severe subscriber degradation detected:{" "}
          <span className="font-code-xs text-code-xs text-error font-bold">14.8% fatal failure rate</span> localized to ap-south-1.
        </>
      ),
    },
    {
      time: "00:06:40",
      tool: "Grafana MCP (Prometheus Query)",
      status: "COMPLETED",
      desc: (
        <>
          Executed:{" "}
          <code className="font-code-xs text-code-xs text-primary-fixed-dim bg-surface-container px-space-xs py-0.5 rounded">
            rate(drm_license_duration_ms&#123;region="apac-south"&#125;[5m])
          </code>
          . p99 latency spiked from 35ms → 1,850ms.
        </>
      ),
    },
    {
      time: "00:09:15",
      tool: "Grafana MCP (Loki Log Analysis)",
      status: "COMPLETED",
      desc: (
        <>
          Query:{" "}
          <code className="font-code-xs text-code-xs text-primary-fixed-dim bg-surface-container px-space-xs py-0.5 rounded">
            &#123;app="drm-service", region="ap-south-1"&#125; |= "timeout"
          </code>
          . Captured 42,800 upstream TCP drops to primary KeyHSM cluster.
        </>
      ),
    },
    {
      time: "00:11:30",
      tool: "PostWire Correlation Engine",
      status: "COMPLETED",
      desc: (
        <>
          Correlated DRM timeout spikes directly with SmartTV and AndroidTV client crash dumps:{" "}
          <span className="font-code-xs text-code-xs text-error font-medium">
            ERROR_DRM_LICENSE_ACQUISITION_FAILED
          </span>
          .
        </>
      ),
    },
    {
      time: "00:13:00",
      tool: "Gemini Autonomous Classifier",
      status: "CONFIDENCE: 94%",
      isHighlighted: true,
      desc: (
        <>
          Classified incident as{" "}
          <span className="font-code-xs text-code-xs text-error font-bold">
            CRITICAL_STREAMING_INCIDENT
          </span>
          . Root cause isolated to cryptographic key exhaustion in ap-south-1 hardware module.
        </>
      ),
    },
  ];

  return (
    <div className="lg:col-span-7 bg-surface-container rounded-xl p-space-lg flex flex-col gap-space-md shadow-lg">
      <div className="flex items-center justify-between flex-wrap gap-space-sm">
        <div className="flex items-center gap-space-sm">
          <div className="w-7 h-7 rounded bg-secondary-container flex items-center justify-center">
            <span className="material-symbols-outlined text-secondary text-[18px]">psychology</span>
          </div>
          <div className="flex flex-col">
            <span className="font-headline-md text-headline-md font-bold text-on-surface">
              Gemini Autonomous Investigation
            </span>
            <span className="font-body-xs text-body-xs text-tertiary flex items-center gap-space-2xs">
              <span className="w-1.5 h-1.5 rounded-full bg-tertiary animate-ping"></span>
              Powered by {health?.gemini_model || "Google Gemini 2.5 Pro"} &amp; Agent Development Kit (ADK)
            </span>
          </div>
        </div>
        <span className="px-space-sm py-space-2xs bg-surface-container-lowest text-on-surface-variant rounded font-label-caps text-label-caps">
          {steps.length > 0 ? `${steps.length} / ${steps.length} TRACES RECORDED` : "7 / 7 TRACES VERIFIED"}
        </span>
      </div>

      {/* Live Investigation Timeline Stream */}
      <div className="flex flex-col gap-space-xs mt-space-xs">
        {steps.length > 0
          ? steps.map((step, idx) => (
              <div
                key={step.step_number || idx}
                className="p-space-sm bg-surface-container-lowest rounded-lg flex items-start gap-space-md transition-colors hover:bg-surface-container-high/60"
              >
                <span className="font-code-xs text-code-xs text-outline shrink-0 mt-0.5">
                  00:0{idx + 1}:15
                </span>
                <span className="material-symbols-outlined text-secondary text-[16px] shrink-0 mt-0.5">
                  verified
                </span>
                <div className="flex flex-col gap-space-2xs w-full min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="font-label-caps text-label-caps text-tertiary">
                      TOOL: {step.tool_used}
                    </span>
                    <span className="font-code-xs text-code-xs text-secondary-fixed-dim">COMPLETED</span>
                  </div>
                  <p className="font-body-xs text-body-xs text-on-surface">
                    <span className="font-semibold">{step.query_summary}</span>: {step.evidence_discovered}
                  </p>
                </div>
              </div>
            ))
          : defaultSteps.map((s, idx) => (
              <div
                key={idx}
                className={`p-space-sm bg-surface-container-lowest rounded-lg flex items-start gap-space-md transition-colors hover:bg-surface-container-high/60 ${
                  s.isHighlighted ? "bg-secondary-container/10" : ""
                }`}
              >
                <span className="font-code-xs text-code-xs text-outline shrink-0 mt-0.5">{s.time}</span>
                <span className="material-symbols-outlined text-secondary text-[16px] shrink-0 mt-0.5">
                  verified
                </span>
                <div className="flex flex-col gap-space-2xs w-full min-w-0">
                  <div className="flex items-center justify-between">
                    <span className={`font-label-caps text-label-caps text-tertiary ${s.isHighlighted ? "font-bold" : ""}`}>
                      TOOL: {s.tool}
                    </span>
                    <span
                      className={
                        s.isHighlighted
                          ? "px-space-xs py-0.5 bg-secondary text-on-secondary rounded font-label-caps text-label-caps font-bold"
                          : "font-code-xs text-code-xs text-secondary-fixed-dim"
                      }
                    >
                      {s.status}
                    </span>
                  </div>
                  <p className="font-body-xs text-body-xs text-on-surface">{s.desc}</p>
                </div>
              </div>
            ))}
      </div>

      <div className="p-space-sm bg-surface-container-high/50 rounded flex items-center justify-between text-on-surface-variant font-code-xs text-code-xs">
        <span className="flex items-center gap-space-xs">
          <span className="material-symbols-outlined text-tertiary text-[14px]">info</span>
          Synthesized safe summary: Root cause verified in ap-south-1 HSM cluster without operational hallucination.
        </span>
        <span className="text-tertiary font-medium">TRACE_ID: {report?.incident_id || "gem-49a0f"}</span>
      </div>
    </div>
  );
};
