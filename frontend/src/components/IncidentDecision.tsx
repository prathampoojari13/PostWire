import React from "react";
import type { IncidentReport } from "../api/client";

interface IncidentDecisionProps {
  report: IncidentReport | null;
  onOpenSimulation: () => void;
  onStatusPost: () => void;
}

export const IncidentDecision: React.FC<IncidentDecisionProps> = ({
  report,
  onOpenSimulation,
  onStatusPost,
}) => {
  const isCritical = report?.classification === "CRITICAL_STREAMING_INCIDENT";
  const confidence = report?.confidence ? Math.round(report.confidence * 100) : 94;

  return (
    <div className="lg:col-span-5 flex flex-col gap-space-md">
      {/* Autonomous Decision Card */}
      <div className="bg-surface-container rounded-xl p-space-lg flex flex-col gap-space-md shadow-lg relative overflow-hidden">
        <div className="flex items-center justify-between">
          <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Incident Classification
          </span>
          <div
            className={`flex items-center gap-space-xs px-space-sm py-space-2xs rounded-full font-label-caps text-label-caps shadow-sm ${
              isCritical ? "bg-error-container text-error" : "bg-secondary-container text-secondary"
            }`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${isCritical ? "bg-error" : "bg-secondary"} animate-ping`}></span>
            <span>{confidence}% CONFIDENCE</span>
          </div>
        </div>

        <div className="flex items-baseline gap-space-sm">
          <span className={`font-headline-lg text-headline-lg font-bold ${isCritical ? "text-error" : "text-secondary"}`}>
            {report?.classification || "CRITICAL_STREAMING_INCIDENT"}
          </span>
        </div>

        <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col gap-space-xs">
          <span className="font-label-caps text-label-caps text-tertiary uppercase">Reason Summary</span>
          <p className="font-body-sm text-body-sm text-on-surface italic">
            "{report?.summary ||
              "Regional DRM degradation is causing catastrophic playback startup failures for APAC-South viewers. Global premiere ingress is only 1.2× baseline, confirming this is an isolated hardware bottleneck, NOT an expected premiere concurrency surge."}"
          </p>
        </div>

        <div className="flex items-center justify-between p-space-sm bg-surface-container-lowest rounded-lg">
          <div className="flex items-center gap-space-sm">
            <span className="material-symbols-outlined text-error text-[20px]">people_alt</span>
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant">IMPACTED ACTIVE VIEWERS</span>
              <span className="font-metric-md text-metric-md text-on-surface font-bold">~184,200 sessions</span>
            </div>
          </div>
          <span className="px-space-sm py-space-2xs bg-surface-container text-outline rounded font-code-xs text-code-xs">
            {report?.affected_region || "ap-south-1"}
          </span>
        </div>
      </div>

      {/* Recommended Mitigation Card */}
      <div className="bg-surface-container rounded-xl p-space-lg flex flex-col gap-space-md shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-space-xs">
            <span className="material-symbols-outlined text-primary-container text-[18px]">build</span>
            <span className="font-headline-md text-headline-md font-bold text-on-surface">Recommended Mitigation</span>
          </div>
          <span className="px-space-xs py-space-2xs bg-primary-container/20 text-primary-container font-label-caps text-label-caps rounded">
            SIMULATED ACTIONS READY
          </span>
        </div>

        <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col gap-space-xs">
          <div className="flex items-center gap-space-xs font-label-caps text-label-caps text-primary">
            <span className="material-symbols-outlined text-[14px]">alt_route</span>
            <span>ACTION PROPOSAL #1</span>
          </div>
          <p className="font-body-sm text-body-sm font-semibold text-on-surface">
            {report?.recommended_mitigation ||
              "Reroute APAC-South SmartTV DRM traffic to secondary key cluster (ap-southeast-1-hsm-b)."}
          </p>
          <span className="font-body-xs text-body-xs text-on-surface-variant mt-space-2xs">
            Estimated mitigation lead time: 90 seconds. Expected viewer QoE normalization to &gt;98.5 within 3 minutes.
          </span>
        </div>

        <div className="p-space-sm bg-surface-container-high/40 rounded flex items-start gap-space-xs text-on-surface-variant font-code-xs text-code-xs">
          <span className="material-symbols-outlined text-outline text-[14px] shrink-0 mt-0.5">shield</span>
          <span>Advisory Mode: Operator authorization is enforced before routing changes push to global Edge Envoy proxies.</span>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-space-sm mt-space-xs">
          <button
            className="px-space-md py-space-sm bg-primary-container hover:bg-primary-container/90 text-on-primary-container font-headline-sm text-headline-sm font-bold rounded shadow flex items-center justify-center gap-space-2xs transition-all"
            onClick={onOpenSimulation}
          >
            <span className="material-symbols-outlined text-[16px]">rule</span>
            <span>Review</span>
          </button>
          <button
            className="px-space-md py-space-sm bg-secondary-container hover:bg-secondary-container/80 text-on-secondary-container font-headline-sm text-headline-sm font-bold rounded shadow flex items-center justify-center gap-space-2xs transition-all"
            onClick={onOpenSimulation}
          >
            <span className="material-symbols-outlined text-[16px]">terminal</span>
            <span>Simulate</span>
          </button>
          <button
            className="px-space-md py-space-sm bg-surface-container-high hover:bg-surface-bright text-on-surface font-headline-sm text-headline-sm font-medium rounded flex items-center justify-center gap-space-2xs transition-all"
            onClick={onStatusPost}
          >
            <span className="material-symbols-outlined text-[16px]">campaign</span>
            <span>Status Post</span>
          </button>
        </div>
      </div>
    </div>
  );
};
