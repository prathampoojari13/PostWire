import React from "react";
import type { IncidentReport, MovieReleaseContext } from "../api/client";

interface IncidentHistoryProps {
  report: IncidentReport | null;
  releaseContext: MovieReleaseContext | null;
  onSimulateReroute: () => void;
  onExportAuditTrail: () => void;
}

export const IncidentHistory: React.FC<IncidentHistoryProps> = ({
  report,
  releaseContext,
  onSimulateReroute,
  onExportAuditTrail,
}) => {
  const isCritical = report?.classification === "CRITICAL_STREAMING_INCIDENT";
  const title = releaseContext?.title || "Neon Tokyo: Origins";

  return (
    <div className="bg-surface-container rounded-xl p-space-lg flex flex-col gap-space-md shadow-lg overflow-x-auto">
      <div className="flex items-center justify-between flex-wrap gap-space-sm">
        <div className="flex items-center gap-space-sm">
          <span className="material-symbols-outlined text-outline text-[20px]">history</span>
          <span className="font-headline-lg text-headline-lg font-bold text-on-surface">
            Autonomous Investigation &amp; Post-Mortem Audit History
          </span>
        </div>
        <div className="flex items-center gap-space-xs">
          <button
            onClick={onExportAuditTrail}
            className="px-space-md py-space-xs bg-surface-container-lowest hover:bg-surface-bright text-on-surface rounded font-body-sm text-body-sm transition-colors"
          >
            Export JSON Audit Trail
          </button>
        </div>
      </div>

      <table className="w-full text-left font-body-sm text-body-sm">
        <thead>
          <tr className="text-on-surface-variant font-label-caps text-label-caps uppercase bg-surface-container-lowest/80 rounded">
            <th className="py-space-sm px-space-md">Timestamp</th>
            <th className="py-space-sm px-space-md">Movie Release</th>
            <th className="py-space-sm px-space-md">Region</th>
            <th className="py-space-sm px-space-md">Incident Trigger</th>
            <th className="py-space-sm px-space-md">Decision Classification</th>
            <th className="py-space-sm px-space-md">Status</th>
            <th className="py-space-sm px-space-md text-right">Operator Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y-0">
          {/* History Row 1: Active Incident */}
          <tr className="bg-surface-container-high/30 hover:bg-surface-container-high/60 transition-colors">
            <td className="py-space-sm px-space-md font-code-xs text-code-xs text-outline font-semibold">
              14:22:10
            </td>
            <td className="py-space-sm px-space-md font-bold text-on-surface">{title}</td>
            <td className="py-space-sm px-space-md font-code-xs text-code-xs text-tertiary">
              {report?.affected_region || "APAC-South"}
            </td>
            <td className="py-space-sm px-space-md text-on-surface">
              {isCritical
                ? "DRM degradation & KeyHSM timeout"
                : "Expected premiere surge volume (8x baseline)"}
            </td>
            <td className="py-space-sm px-space-md">
              <span
                className={`px-space-xs py-space-2xs rounded font-label-caps text-label-caps font-bold ${
                  isCritical ? "bg-error-container text-error" : "bg-secondary-container text-secondary"
                }`}
              >
                {isCritical ? "🔴 CRITICAL_STREAMING" : "🟢 EXPECTED_PREMIERE"}
              </span>
            </td>
            <td className="py-space-sm px-space-md">
              <span
                className={`flex items-center gap-space-2xs font-code-xs text-code-xs font-bold ${
                  isCritical ? "text-error" : "text-secondary"
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${isCritical ? "bg-error animate-pulse" : "bg-secondary"}`}></span>
                {isCritical ? "Active Investigation" : "Resolved (Auto-Closed)"}
              </span>
            </td>
            <td className="py-space-sm px-space-md text-right">
              {isCritical ? (
                <button
                  className="px-space-sm py-space-xs bg-primary-container text-on-primary-container hover:bg-primary-container/90 rounded font-code-xs text-code-xs font-bold transition-colors"
                  onClick={onSimulateReroute}
                >
                  Simulate Reroute
                </button>
              ) : (
                <span className="text-outline font-code-xs text-code-xs">No Action Needed</span>
              )}
            </td>
          </tr>

          {/* History Row 2: CyberDune 2 */}
          <tr className="hover:bg-surface-container-high/40 transition-colors">
            <td className="py-space-sm px-space-md font-code-xs text-code-xs text-outline">11:05:40</td>
            <td className="py-space-sm px-space-md font-medium text-on-surface">CyberDune 2</td>
            <td className="py-space-sm px-space-md font-code-xs text-code-xs text-outline">Global</td>
            <td className="py-space-sm px-space-md text-on-surface-variant">
              Massive premiere concurrency spike (11.4×)
            </td>
            <td className="py-space-sm px-space-md">
              <span className="px-space-xs py-space-2xs bg-secondary-container/40 text-secondary rounded font-label-caps text-label-caps">
                🟢 EXPECTED_PREMIERE
              </span>
            </td>
            <td className="py-space-sm px-space-md">
              <span className="text-secondary font-code-xs text-code-xs">Resolved (Auto-Closed)</span>
            </td>
            <td className="py-space-sm px-space-md text-right">
              <span className="text-outline font-code-xs text-code-xs">No Action Needed</span>
            </td>
          </tr>

          {/* History Row 3: Stellar Odyssey */}
          <tr className="hover:bg-surface-container-high/40 transition-colors">
            <td className="py-space-sm px-space-md font-code-xs text-code-xs text-outline">08:45:12</td>
            <td className="py-space-sm px-space-md font-medium text-on-surface">Stellar Odyssey</td>
            <td className="py-space-sm px-space-md font-code-xs text-code-xs text-outline">LATAM</td>
            <td className="py-space-sm px-space-md text-on-surface-variant">Transcoder chunk buffer drift</td>
            <td className="py-space-sm px-space-md">
              <span className="px-space-xs py-space-2xs bg-surface-bright text-primary-fixed-dim rounded font-label-caps text-label-caps">
                🟡 INVESTIGATE
              </span>
            </td>
            <td className="py-space-sm px-space-md">
              <span className="text-on-surface-variant font-code-xs text-code-xs">Mitigated</span>
            </td>
            <td className="py-space-sm px-space-md text-right">
              <span className="px-space-sm py-0.5 bg-surface-container-lowest text-tertiary rounded font-code-xs text-code-xs">
                CDN Warm-up Done
              </span>
            </td>
          </tr>

          {/* History Row 4: The Quantum Heist */}
          <tr className="hover:bg-surface-container-high/40 transition-colors">
            <td className="py-space-sm px-space-md font-code-xs text-code-xs text-outline">Yesterday</td>
            <td className="py-space-sm px-space-md font-medium text-on-surface">The Quantum Heist</td>
            <td className="py-space-sm px-space-md font-code-xs text-code-xs text-outline">EU-West</td>
            <td className="py-space-sm px-space-md text-on-surface-variant">Origin shield transient 502 blip</td>
            <td className="py-space-sm px-space-md">
              <span className="px-space-xs py-space-2xs bg-secondary-container/40 text-secondary rounded font-label-caps text-label-caps">
                🟢 EXPECTED_PREMIERE
              </span>
            </td>
            <td className="py-space-sm px-space-md">
              <span className="text-secondary font-code-xs text-code-xs">Resolved</span>
            </td>
            <td className="py-space-sm px-space-md text-right">
              <span className="text-outline font-code-xs text-code-xs">Cache Shield Rerouted</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};
