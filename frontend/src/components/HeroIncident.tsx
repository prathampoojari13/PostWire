import React from "react";
import type { AggregateTelemetry, MovieReleaseContext, IncidentReport } from "../api/client";

interface HeroIncidentProps {
  report: IncidentReport | null;
  releaseContext: MovieReleaseContext | null;
  qoe: AggregateTelemetry | null;
  onEscalate: () => void;
}

export const HeroIncident: React.FC<HeroIncidentProps> = ({
  report,
  releaseContext,
  qoe,
  onEscalate,
}) => {
  const isCritical = report?.classification === "CRITICAL_STREAMING_INCIDENT";
  const isFallback =
    report?.summary.toLowerCase().includes("fallback") ||
    report?.summary.toLowerCase().includes("quota");

  const playbackFailureStr = qoe ? `${(qoe.avg_playback_failure_rate * 100).toFixed(1)}%` : "14.8%";
  const ebvsStr = qoe ? `${(qoe.avg_exit_before_video_start * 100).toFixed(1)}%` : "9.2%";
  const drmLatencyStr = qoe ? `${Math.round(qoe.avg_drm_license_latency_ms).toLocaleString()} ms` : "1,850 ms";
  const http5xxStr = qoe ? `${(qoe.avg_http_5xx_rate * 100).toFixed(1)}%` : "8.4%";
  const surgeStr = releaseContext ? `${releaseContext.expected_viewer_surge_factor.toFixed(1)}×` : "1.2×";

  return (
    <div id="section-overview" className="relative overflow-hidden rounded-xl bg-surface-container p-space-lg xl:p-space-xl shadow-xl flex flex-col gap-space-lg">
      <div
        className={`absolute -right-24 -top-24 w-96 h-96 rounded-full blur-3xl pointer-events-none ${
          isCritical ? "bg-error-container/20" : "bg-secondary-container/20"
        }`}
      ></div>
      <div className="absolute -left-20 -bottom-20 w-80 h-80 bg-primary-container/10 rounded-full blur-3xl pointer-events-none"></div>

      {/* Header & Metadata Bar */}
      <div className="relative z-10 flex flex-col xl:flex-row xl:items-center justify-between gap-space-md">
        <div className="flex flex-wrap items-center gap-space-md">
          <div
            className={`flex items-center gap-space-xs px-space-md py-space-xs rounded font-label-caps text-label-caps uppercase shadow-sm ${
              isCritical
                ? "bg-error-container text-error animate-pulse"
                : "bg-secondary-container text-secondary"
            }`}
          >
            <span className="material-symbols-outlined text-[14px]">
              {isCritical ? "crisis_alert" : "verified"}
            </span>
            <span>{report ? report.classification.replace(/_/g, " ") : "CRITICAL STREAMING INCIDENT"}</span>
          </div>

          <span className="font-headline-xl text-headline-xl font-bold tracking-tight text-on-surface">
            {releaseContext ? releaseContext.title : "Neon Tokyo: Origins"}
          </span>

          <div className="flex items-center gap-space-xs px-space-sm py-space-2xs bg-surface-container-high rounded text-on-surface-variant font-code-xs text-code-xs">
            <span className="material-symbols-outlined text-[13px] text-outline">movie</span>
            <span>ID: {releaseContext ? releaseContext.release_id : "rel_neontokyo_2026"}</span>
          </div>

          <div className="flex items-center gap-space-xs px-space-sm py-space-2xs bg-surface-container-high rounded text-on-surface-variant font-code-xs text-code-xs">
            <span className="material-symbols-outlined text-[13px] text-tertiary">public</span>
            <span>{report?.affected_region ? `APAC-South (${report.affected_region})` : "APAC-South (ap-south-1)"}</span>
          </div>
        </div>

        <div className="flex items-center gap-space-md flex-wrap">
          <div className="flex items-center gap-space-xs px-space-md py-space-xs bg-surface-container-lowest rounded font-code-xs text-code-xs">
            <span className="text-on-surface-variant">RULE:</span>
            <span className={`font-semibold ${isCritical ? "text-error" : "text-secondary"}`}>
              {isCritical ? "REGIONAL_QOE_DEGRADATION" : "PREMIERE_AUTO_ABSORB"}
            </span>
          </div>

          <div className="flex items-center gap-space-xs px-space-md py-space-xs bg-surface-container-lowest rounded font-code-xs text-code-xs">
            <span className="material-symbols-outlined text-[14px] text-primary">timer</span>
            <span className="text-on-surface-variant">ELAPSED:</span>
            <span className="text-on-surface font-bold text-metric-md">00:14:22</span>
          </div>

          <button
            onClick={onEscalate}
            className="px-space-md py-space-xs bg-surface-container-high hover:bg-surface-bright text-on-surface rounded font-body-sm text-body-sm flex items-center gap-space-xs transition-colors"
          >
            <span className="material-symbols-outlined text-[16px]">share</span>
            <span>Escalate P0</span>
          </button>
        </div>
      </div>

      {/* Differentiated Callout Banner */}
      <div className="relative z-10 flex items-center gap-space-md p-space-md rounded-lg bg-surface-container-lowest">
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
            isCritical ? "bg-error/20" : "bg-secondary/20"
          }`}
        >
          <span className={`material-symbols-outlined text-[18px] ${isCritical ? "text-error" : "text-secondary"}`}>
            {isCritical ? "warning" : "check_circle"}
          </span>
        </div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-sm w-full">
          <div className="flex flex-col">
            <span className={`font-headline-sm text-headline-sm font-semibold ${isCritical ? "text-error" : "text-secondary"}`}>
              {isCritical
                ? "Incident Differentiated: Infrastructure Failure, Not Premiere Load Surge"
                : "Expected Premiere Concurrency Surge: Zero Edge Degradation"}
            </span>
            <span className="font-body-sm text-body-sm text-on-surface-variant">
              {report?.summary ||
                "Global premiere traffic ingress is currently measured at nominal baseline while regional QoE degradation hit catastrophic levels in ap-south-1."}
            </span>
          </div>

          <div className="flex items-center gap-space-xs shrink-0 font-label-caps text-label-caps px-space-sm py-space-2xs bg-surface-container-high rounded text-tertiary">
            <span className="material-symbols-outlined text-[14px]">
              {isFallback ? "shield" : "auto_awesome"}
            </span>
            <span>{isFallback ? "SAFETY FALLBACK DIAGNOSED" : "GEMINI DIAGNOSED"}</span>
          </div>
        </div>
      </div>

      {/* High-Density Telemetry Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-space-md relative z-10">
        {/* Metric 1: Playback Failure (Regional Slice) */}
        <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">
              {isCritical ? "Playback Failure (SmartTV)" : "Global Playback Failure"}
            </span>
            <span className="px-space-xs py-space-2xs bg-error-container text-error rounded font-code-xs text-code-xs">
              SLA: 1.2%
            </span>
          </div>
          <div className="flex items-baseline justify-between mt-space-sm">
            <span className={`font-metric-display text-metric-display font-bold tracking-tight ${isCritical ? "text-error" : "text-secondary"}`}>
              {isCritical ? "14.8%" : playbackFailureStr}
            </span>
            <span className={`font-code-xs text-code-xs font-medium ${isCritical ? "text-error" : "text-secondary"}`}>
              {isCritical ? "+13.6% over SLA" : "Within SLA"}
            </span>
          </div>
          <div className="w-full bg-surface-container-highest h-1 rounded mt-space-sm overflow-hidden">
            <div
              className={`h-full rounded ${isCritical ? "bg-error" : "bg-secondary"}`}
              style={{ width: isCritical ? "86%" : "12%" }}
            ></div>
          </div>
        </div>

        {/* Metric 2: EBVS */}
        <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">EBVS (Exit Before Start)</span>
            <span className="px-space-xs py-space-2xs bg-error-container text-error rounded font-code-xs text-code-xs">
              Normal &lt; 1%
            </span>
          </div>
          <div className="flex items-baseline justify-between mt-space-sm">
            <span className={`font-metric-display text-metric-display font-bold tracking-tight ${isCritical ? "text-error" : "text-secondary"}`}>
              {isCritical ? "9.2%" : ebvsStr}
            </span>
            <span className={`font-code-xs text-code-xs font-medium ${isCritical ? "text-error" : "text-secondary"}`}>
              {isCritical ? "9.2× threshold" : "Nominal"}
            </span>
          </div>
          <div className="w-full bg-surface-container-highest h-1 rounded mt-space-sm overflow-hidden">
            <div
              className={`h-full rounded ${isCritical ? "bg-error" : "bg-secondary"}`}
              style={{ width: isCritical ? "72%" : "8%" }}
            ></div>
          </div>
        </div>

        {/* Metric 3: DRM Latency */}
        <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">
              {isCritical ? "DRM Latency (p99 APAC)" : "DRM License Latency"}
            </span>
            <span className="px-space-xs py-space-2xs bg-surface-container-high text-primary rounded font-code-xs text-code-xs">
              Base: 35ms
            </span>
          </div>
          <div className="flex items-baseline justify-between mt-space-sm">
            <span className="font-metric-display text-metric-display text-primary font-bold tracking-tight">
              {isCritical ? "1,850 ms" : drmLatencyStr}
            </span>
            <span className="font-code-xs text-code-xs text-primary font-medium">
              {isCritical ? "52× surge" : "Nominal"}
            </span>
          </div>
          <div className="w-full bg-surface-container-highest h-1 rounded mt-space-sm overflow-hidden">
            <div
              className="bg-primary h-full rounded"
              style={{ width: isCritical ? "95%" : "15%" }}
            ></div>
          </div>
        </div>

        {/* Metric 4: HTTP 504 Timeouts */}
        <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">HTTP 504 Timeouts (Key HSM)</span>
            <span className="px-space-xs py-space-2xs bg-surface-container-high text-on-surface-variant rounded font-code-xs text-code-xs">
              Key HSM
            </span>
          </div>
          <div className="flex items-baseline justify-between mt-space-sm">
            <span className={`font-metric-display text-metric-display font-bold tracking-tight ${isCritical ? "text-error" : "text-secondary"}`}>
              {isCritical ? "8.4%" : http5xxStr}
            </span>
            <span className={`font-code-xs text-code-xs font-medium ${isCritical ? "text-error" : "text-secondary"}`}>
              {isCritical ? "Elevated" : "Zero Errors"}
            </span>
          </div>
          <div className="w-full bg-surface-container-highest h-1 rounded mt-space-sm overflow-hidden">
            <div
              className={`h-full rounded ${isCritical ? "bg-error" : "bg-secondary"}`}
              style={{ width: isCritical ? "60%" : "2%" }}
            ></div>
          </div>
        </div>

        {/* Metric 5: Global Ingress Traffic */}
        <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between shadow-sm">
          <div className="flex items-center justify-between">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Global Ingress Traffic</span>
            <span className="px-space-xs py-space-2xs bg-surface-container-high text-tertiary rounded font-code-xs text-code-xs">
              {isCritical ? "Non-Surge" : "Surge Ingress"}
            </span>
          </div>
          <div className="flex items-baseline justify-between mt-space-sm">
            <span className="font-metric-display text-metric-display text-on-surface font-bold tracking-tight">
              {surgeStr}
            </span>
            <span className="font-code-xs text-code-xs text-tertiary font-medium">
              Expected: 8.0×
            </span>
          </div>
          <div className="w-full bg-surface-container-highest h-1 rounded mt-space-sm overflow-hidden">
            <div
              className="bg-tertiary h-full rounded"
              style={{ width: isCritical ? "25%" : "95%" }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};
