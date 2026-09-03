import React from "react";
import type { AggregateTelemetry, RegionalQoEBreakdown, IncidentReport } from "../api/client";

interface RegionalQoEProps {
  qoe: AggregateTelemetry | null;
  regionalBreakdown: RegionalQoEBreakdown[];
  report: IncidentReport | null;
}

export const RegionalQoE: React.FC<RegionalQoEProps> = ({
  qoe,
  regionalBreakdown,
  report,
}) => {
  const isCritical = report?.classification === "CRITICAL_STREAMING_INCIDENT";
  const visScore = qoe ? Math.round(qoe.viewer_impact_score) : 91;

  // Static regions from Stitch if backend regional breakdown is empty
  const defaultRegions = [
    {
      region: "APAC-South (ap-south-1)",
      score: "91 / 100",
      failure: "14.8%",
      latency: "1,850 ms",
      traffic: "1.2×",
      status: "🔴 CRITICAL",
      isCritical: true,
    },
    {
      region: "Europe (eu-central-1)",
      score: "18 / 100",
      failure: "0.4%",
      latency: "28 ms",
      traffic: "7.8×",
      status: "🟢 HEALTHY",
      isCritical: false,
    },
    {
      region: "North America (us-east-1)",
      score: "12 / 100",
      failure: "0.3%",
      latency: "22 ms",
      traffic: "9.4×",
      status: "🟢 HEALTHY",
      isCritical: false,
    },
    {
      region: "APAC-East (ap-northeast-1)",
      score: "24 / 100",
      failure: "0.8%",
      latency: "42 ms",
      traffic: "4.1×",
      status: "🟢 HEALTHY",
      isCritical: false,
    },
    {
      region: "Latin America (sa-east-1)",
      score: "15 / 100",
      failure: "0.5%",
      latency: "38 ms",
      traffic: "3.2×",
      status: "🟢 HEALTHY",
      isCritical: false,
    },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
      {/* QoE Score Gauge & Sub-Dimensions (4 Cols) */}
      <div className="lg:col-span-4 bg-surface-container rounded-xl p-space-lg flex flex-col justify-between gap-space-md shadow-lg">
        <div className="flex items-center justify-between">
          <span className="font-headline-md text-headline-md font-bold text-on-surface">
            Viewer QoE Health Score
          </span>
          <span
            className={`px-space-xs py-space-2xs rounded font-label-caps text-label-caps ${
              isCritical ? "bg-error-container text-error" : "bg-secondary-container text-secondary"
            }`}
          >
            {isCritical ? "DEGRADED" : "HEALTHY"}
          </span>
        </div>

        {/* Gauge Visual */}
        <div className="flex items-center justify-center p-space-md">
          <div className="relative flex items-center justify-center w-40 h-40">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle
                className="text-surface-container-highest"
                cx="50"
                cy="50"
                fill="transparent"
                r="40"
                stroke="currentColor"
                strokeWidth="8"
              ></circle>
              <circle
                className={`${isCritical ? "text-error" : "text-secondary"} transition-all duration-1000`}
                cx="50"
                cy="50"
                fill="transparent"
                r="40"
                stroke="currentColor"
                strokeDasharray="251.2"
                strokeDashoffset={isCritical ? "30" : "210"}
                strokeLinecap="round"
                strokeWidth="8"
              ></circle>
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className={`font-metric-display text-metric-display font-extrabold leading-none ${isCritical ? "text-error" : "text-secondary"}`}>
                {visScore}
              </span>
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase mt-1">
                Impact Score
              </span>
              <span className={`font-code-xs text-code-xs font-semibold ${isCritical ? "text-error" : "text-secondary"}`}>
                {isCritical ? "Critical Impact" : "Healthy QoE"}
              </span>
            </div>
          </div>
        </div>

        {/* QoE Dimension Bars */}
        <div className="flex flex-col gap-space-sm">
          <div>
            <div className="flex items-center justify-between font-body-xs text-body-xs">
              <span className="text-on-surface">Playback Failures</span>
              <span className={`font-code-xs text-code-xs font-bold ${isCritical ? "text-error" : "text-secondary"}`}>
                {isCritical ? "94 / 100 (Critical)" : "08 / 100 (Healthy)"}
              </span>
            </div>
            <div className="w-full bg-surface-container-highest h-1.5 rounded mt-1">
              <div className={`h-full rounded ${isCritical ? "bg-error" : "bg-secondary"}`} style={{ width: isCritical ? "94%" : "8%" }}></div>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between font-body-xs text-body-xs">
              <span className="text-on-surface">DRM License Failures</span>
              <span className={`font-code-xs text-code-xs font-bold ${isCritical ? "text-error" : "text-secondary"}`}>
                {isCritical ? "98 / 100 (Critical)" : "04 / 100 (Healthy)"}
              </span>
            </div>
            <div className="w-full bg-surface-container-highest h-1.5 rounded mt-1">
              <div className={`h-full rounded ${isCritical ? "bg-error" : "bg-secondary"}`} style={{ width: isCritical ? "98%" : "4%" }}></div>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between font-body-xs text-body-xs">
              <span className="text-on-surface">Startup Latency</span>
              <span className="font-code-xs text-code-xs text-primary font-bold">
                {isCritical ? "82 / 100 (Elevated)" : "12 / 100 (Nominal)"}
              </span>
            </div>
            <div className="w-full bg-surface-container-highest h-1.5 rounded mt-1">
              <div className="bg-primary h-full rounded" style={{ width: isCritical ? "82%" : "12%" }}></div>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between font-body-xs text-body-xs">
              <span className="text-on-surface">Rebuffering Ratio</span>
              <span className="font-code-xs text-code-xs text-secondary font-bold">14 / 100 (Healthy)</span>
            </div>
            <div className="w-full bg-surface-container-highest h-1.5 rounded mt-1">
              <div className="bg-secondary h-full rounded" style={{ width: "14%" }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Regional Impact Matrix Table (8 Cols) */}
      <div className="lg:col-span-8 bg-surface-container rounded-xl p-space-lg flex flex-col justify-between gap-space-md shadow-lg overflow-x-auto">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-space-xs">
            <span className="material-symbols-outlined text-outline text-[18px]">public</span>
            <span className="font-headline-md text-headline-md font-bold text-on-surface">
              Regional Impact Matrix
            </span>
          </div>
          <span className="font-code-xs text-code-xs text-on-surface-variant">5 Edge Availability Zones</span>
        </div>

        <table className="w-full text-left font-body-sm text-body-sm">
          <thead>
            <tr className="text-on-surface-variant font-label-caps text-label-caps uppercase bg-surface-container-lowest/70 rounded">
              <th className="py-space-sm px-space-md">Edge Region</th>
              <th className="py-space-sm px-space-md">Impact Score</th>
              <th className="py-space-sm px-space-md">Playback Failures</th>
              <th className="py-space-sm px-space-md">DRM Latency</th>
              <th className="py-space-sm px-space-md">Traffic Ratio</th>
              <th className="py-space-sm px-space-md text-right">Cluster Status</th>
            </tr>
          </thead>
          <tbody className="divide-y-0">
            {regionalBreakdown && regionalBreakdown.length > 0
              ? regionalBreakdown.map((row) => {
                  const regCritical = row.status === "CRITICAL";
                  return (
                    <tr
                      key={row.region}
                      className={`transition-colors ${
                        regCritical ? "bg-error-container/15 hover:bg-error-container/25" : "hover:bg-surface-container-high/40"
                      }`}
                    >
                      <td className="py-space-sm px-space-md font-semibold text-on-surface flex items-center gap-space-xs">
                        {regCritical && <span className="w-2 h-2 rounded-full bg-error animate-ping"></span>}
                        <span>{row.region}</span>
                      </td>
                      <td className={`py-space-sm px-space-md font-code-sm text-code-sm font-bold ${regCritical ? "text-error" : "text-secondary"}`}>
                        {Math.round(row.viewer_impact_score)} / 100
                      </td>
                      <td className={`py-space-sm px-space-md font-code-sm text-code-sm font-bold ${regCritical ? "text-error" : "text-secondary"}`}>
                        {(row.playback_failure_rate * 100).toFixed(1)}%
                      </td>
                      <td className={`py-space-sm px-space-md font-code-sm text-code-sm font-bold ${regCritical ? "text-primary" : "text-on-surface-variant"}`}>
                        {Math.round(row.drm_license_latency_ms)} ms
                      </td>
                      <td className="py-space-sm px-space-md font-code-sm text-code-sm text-on-surface">
                        {regCritical ? "1.2×" : "8.1×"}
                      </td>
                      <td className="py-space-sm px-space-md text-right">
                        <span
                          className={`px-space-xs py-space-2xs rounded font-label-caps text-label-caps font-bold ${
                            regCritical ? "bg-error-container text-error" : "bg-secondary-container/30 text-secondary"
                          }`}
                        >
                          {regCritical ? "🔴 CRITICAL" : "🟢 HEALTHY"}
                        </span>
                      </td>
                    </tr>
                  );
                })
              : defaultRegions.map((row, idx) => (
                  <tr
                    key={idx}
                    className={`transition-colors ${
                      row.isCritical ? "bg-error-container/15 hover:bg-error-container/25" : "hover:bg-surface-container-high/40"
                    }`}
                  >
                    <td className="py-space-sm px-space-md font-semibold text-on-surface flex items-center gap-space-xs">
                      {row.isCritical && <span className="w-2 h-2 rounded-full bg-error animate-ping"></span>}
                      <span>{row.region}</span>
                    </td>
                    <td className={`py-space-sm px-space-md font-code-sm text-code-sm font-bold ${row.isCritical ? "text-error" : "text-secondary"}`}>
                      {row.score}
                    </td>
                    <td className={`py-space-sm px-space-md font-code-sm text-code-sm font-bold ${row.isCritical ? "text-error" : "text-secondary"}`}>
                      {row.failure}
                    </td>
                    <td className={`py-space-sm px-space-md font-code-sm text-code-sm font-bold ${row.isCritical ? "text-primary" : "text-on-surface-variant"}`}>
                      {row.latency}
                    </td>
                    <td className="py-space-sm px-space-md font-code-sm text-code-sm text-on-surface">
                      {row.traffic}
                    </td>
                    <td className="py-space-sm px-space-md text-right">
                      <span
                        className={`px-space-xs py-space-2xs rounded font-label-caps text-label-caps font-bold ${
                          row.isCritical ? "bg-error-container text-error" : "bg-secondary-container/30 text-secondary"
                        }`}
                      >
                        {row.status}
                      </span>
                    </td>
                  </tr>
                ))}
          </tbody>
        </table>

        <div className="p-space-sm bg-surface-container-lowest rounded flex items-center justify-between text-on-surface-variant font-code-xs text-code-xs">
          <span>Telemetry aggregated over 14.2M simultaneous global stream sessions</span>
          <span className="text-tertiary">SLA Target: 99.99% QoE Integrity</span>
        </div>
      </div>
    </div>
  );
};
