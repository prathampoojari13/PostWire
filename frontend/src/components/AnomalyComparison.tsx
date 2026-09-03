import React from "react";
import type { AggregateTelemetry, MovieReleaseContext, IncidentReport } from "../api/client";

interface AnomalyComparisonProps {
  report: IncidentReport | null;
  releaseContext: MovieReleaseContext | null;
  qoe: AggregateTelemetry | null;
}

export const AnomalyComparison: React.FC<AnomalyComparisonProps> = ({
  report,
  releaseContext,
  qoe,
}) => {
  const isCritical = report?.classification === "CRITICAL_STREAMING_INCIDENT";
  const title = releaseContext?.title || "Neon Tokyo: Origins";

  return (
    <div className="bg-surface-container rounded-xl p-space-lg flex flex-col gap-space-lg shadow-lg">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-xs">
        <div className="flex items-center gap-space-sm">
          <span className="material-symbols-outlined text-tertiary text-[22px]">compare_arrows</span>
          <span className="font-headline-lg text-headline-lg font-bold text-on-surface">
            Gemini Anomaly Differentiation Model
          </span>
        </div>
        <span className="font-code-xs text-code-xs text-on-surface-variant">
          PostWire ML-Class #PRM-8839 • Trained on 12,000+ Worldwide Premieres
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-space-lg">
        {/* Left: Normal Expected Premiere Surge */}
        <div className="bg-surface-container-lowest rounded-xl p-space-lg flex flex-col justify-between gap-space-md shadow-sm opacity-90 hover:opacity-100 transition-opacity">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-space-xs">
              <span className="material-symbols-outlined text-secondary text-[20px]">check_circle</span>
              <span className="font-headline-md text-headline-md font-bold text-on-surface">
                Standard Expected Premiere Surge
              </span>
            </div>
            <span className="px-space-xs py-space-2xs bg-secondary-container/30 text-secondary rounded font-label-caps text-label-caps">
              BASELINE NORM
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-space-sm p-space-md bg-surface-container rounded-lg">
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant">TRAFFIC</span>
              <span className="font-metric-md text-metric-md text-on-surface font-bold">8.0× Base</span>
            </div>
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant">QOE SCORE</span>
              <span className="font-metric-md text-metric-md text-secondary font-bold">98.8</span>
            </div>
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant">CDN CACHE</span>
              <span className="font-metric-md text-metric-md text-on-surface font-bold">97.5%</span>
            </div>
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant">FAIL RATE</span>
              <span className="font-metric-md text-metric-md text-secondary font-bold">0.6%</span>
            </div>
          </div>

          <p className="font-body-sm text-body-sm text-on-surface-variant">
            Content distribution architecture absorbs global concurrency smoothly. Key HSM caches pre-warm keys; auto-scaler expands egress nodes with zero perceptible user degradation.
          </p>

          <div className="flex items-center justify-between pt-space-xs">
            <span className="px-space-sm py-space-xs bg-secondary-container/40 text-secondary font-code-sm text-code-sm font-bold rounded">
              🟢 EXPECTED_PREMIERE_SURGE
            </span>
            <span className="font-code-xs text-code-xs text-outline">Action: Auto-Absorb</span>
          </div>
        </div>

        {/* Right: Current Incident */}
        <div className="bg-surface-container-lowest rounded-xl p-space-lg flex flex-col justify-between gap-space-md shadow-sm relative overflow-hidden">
          <div className={`absolute top-0 left-0 right-0 h-1 ${isCritical ? "bg-error" : "bg-secondary"}`}></div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-space-xs">
              <span className={`material-symbols-outlined text-[20px] ${isCritical ? "text-error" : "text-secondary"}`}>
                {isCritical ? "dangerous" : "verified"}
              </span>
              <span className={`font-headline-md text-headline-md font-bold ${isCritical ? "text-error" : "text-secondary"}`}>
                Current: {title}
              </span>
            </div>
            <span
              className={`px-space-xs py-space-2xs rounded font-label-caps text-label-caps ${
                isCritical ? "bg-error-container text-error animate-pulse" : "bg-secondary-container text-secondary"
              }`}
            >
              {isCritical ? "ACTIVE INCIDENT" : "NOMINAL SURGE"}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-space-sm p-space-md bg-surface-container rounded-lg">
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant">TRAFFIC</span>
              <span className="font-metric-md text-metric-md text-on-surface font-bold">
                {releaseContext ? `${releaseContext.expected_viewer_surge_factor.toFixed(1)}× Base` : "1.2× Base"}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant">QOE SCORE</span>
              <span className={`font-metric-md text-metric-md font-bold ${isCritical ? "text-error" : "text-secondary"}`}>
                {qoe ? `${Math.round(qoe.viewer_impact_score)} / 100` : "91 / 100"}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant">DRM LATENCY</span>
              <span className="font-metric-md text-metric-md text-primary font-bold">
                {qoe ? `${Math.round(qoe.avg_drm_license_latency_ms).toLocaleString()} ms` : "1,850 ms"}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant">FAIL RATE</span>
              <span className={`font-metric-md text-metric-md font-bold ${isCritical ? "text-error" : "text-secondary"}`}>
                {qoe ? `${(qoe.avg_playback_failure_rate * 100).toFixed(1)}%` : "14.8%"}
              </span>
            </div>
          </div>

          <p className="font-body-sm text-body-sm text-on-surface">
            {isCritical
              ? "Severe localized infrastructure collapse masquerading as debut load. Root failure is key exhaustion on primary ap-south HSM, causing client DRM timeouts prior to segment playback."
              : "Global premiere concurrency surge running normally. Infrastructure auto-scales and key distribution is nominal."}
          </p>

          <div className="flex items-center justify-between pt-space-xs">
            <span
              className={`px-space-sm py-space-xs font-code-sm text-code-sm font-bold rounded ${
                isCritical ? "bg-error-container text-error" : "bg-secondary-container/40 text-secondary"
              }`}
            >
              {isCritical ? "🔴 CRITICAL_STREAMING_INCIDENT" : "🟢 EXPECTED_PREMIERE_SURGE"}
            </span>
            <span className={`font-code-xs text-code-xs font-medium ${isCritical ? "text-error" : "text-secondary"}`}>
              {isCritical ? "Immediate Reroute Required" : "Action: Auto-Absorb"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
