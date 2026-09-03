import React from "react";
import type { AggregateTelemetry, HealthStatus } from "../api/client";

interface GrafanaObservabilityProps {
  qoe: AggregateTelemetry | null;
  health: HealthStatus | null;
  onRefresh: () => void;
}

export const GrafanaObservability: React.FC<GrafanaObservabilityProps> = ({
  qoe,
  health,
  onRefresh,
}) => {
  const viewersStr = qoe
    ? `${(qoe.total_concurrent_viewers / 1_000_000).toFixed(2)}M`
    : "1.41M";
  const drmLatencyStr = qoe
    ? `${Math.round(qoe.avg_drm_license_latency_ms).toLocaleString()} ms`
    : "1,850 ms";
  const playbackFailureStr = qoe
    ? `${(qoe.avg_playback_failure_rate * 100).toFixed(1)}%`
    : "14.8%";
  const cdnCacheStr = qoe
    ? `${(qoe.avg_cdn_cache_hit_ratio * 100).toFixed(1)}%`
    : "96.2%";
  const http504Str = qoe
    ? `${(qoe.avg_http_5xx_rate * 100).toFixed(1)}%`
    : "8.4%";

  return (
    <div className="bg-surface-container rounded-xl p-space-lg flex flex-col gap-space-lg shadow-lg">
      {/* Observability Header & Filter Toolbar */}
      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-space-md">
        <div className="flex items-center gap-space-sm">
          <div className="w-7 h-7 rounded bg-surface-container-high flex items-center justify-center">
            <span className="material-symbols-outlined text-primary-container text-[18px]">show_chart</span>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-space-xs">
              <span className="font-headline-md text-headline-md font-bold text-on-surface">
                Grafana Observability &amp; Telemetry Feed
              </span>
              <span className="px-space-xs py-space-2xs bg-surface-container-lowest text-tertiary rounded font-label-caps text-label-caps">
                {health?.grafana_mcp_mode === "live" ? "LIVE • GRAFANA MCP" : "MOCK • GRAFANA MCP"}
              </span>
            </div>
            <span className="font-body-xs text-body-xs text-on-surface-variant">
              Prometheus TSDB + Loki streaming at 5-second polling interval
            </span>
          </div>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-space-xs flex-wrap">
          <div className="flex items-center gap-space-xs bg-surface-container-lowest px-space-sm py-space-xs rounded text-body-xs font-body-xs text-on-surface">
            <span className="text-on-surface-variant">Region:</span>
            <span className="font-semibold text-primary">APAC-South (ap-south-1)</span>
            <span className="material-symbols-outlined text-[14px] text-outline">expand_more</span>
          </div>
          <div className="flex items-center gap-space-xs bg-surface-container-lowest px-space-sm py-space-xs rounded text-body-xs font-body-xs text-on-surface">
            <span className="text-on-surface-variant">Device:</span>
            <span className="font-semibold">All Devices</span>
            <span className="material-symbols-outlined text-[14px] text-outline">expand_more</span>
          </div>
          <div className="flex items-center gap-space-xs bg-surface-container-lowest px-space-sm py-space-xs rounded text-body-xs font-body-xs text-on-surface">
            <span className="text-on-surface-variant">Window:</span>
            <span className="font-semibold">Last 1h (5m bucket)</span>
            <span className="material-symbols-outlined text-[14px] text-outline">expand_more</span>
          </div>
          <button
            onClick={onRefresh}
            className="p-space-xs bg-surface-container-lowest hover:bg-surface-bright rounded text-on-surface transition-colors"
            title="Refresh Grafana Telemetry"
          >
            <span className="material-symbols-outlined text-[16px]">refresh</span>
          </button>
        </div>
      </div>

      {/* Telemetry Charts Bento (4 dense charts) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-space-md">
        {/* Chart 1: Concurrent Viewers */}
        <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between gap-space-md shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">
                Concurrent Viewers (APAC)
              </span>
              <span className="font-metric-md text-metric-md text-on-surface font-bold">
                {viewersStr} <span className="font-body-xs text-body-xs font-normal text-error">↓ -18%</span>
              </span>
            </div>
            <span className="material-symbols-outlined text-outline text-[18px]">group</span>
          </div>
          {/* Sparkline Chart (SVG) */}
          <div className="h-24 w-full flex items-end">
            <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 240 70">
              <defs>
                <linearGradient id="grad-viewers" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#ffb690" stopOpacity="0.3"></stop>
                  <stop offset="100%" stopColor="#ffb690" stopOpacity="0.0"></stop>
                </linearGradient>
              </defs>
              <path
                className="text-primary"
                d="M0,50 Q30,48 60,40 T120,20 T180,25 T240,55"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              ></path>
              <path
                d="M0,50 Q30,48 60,40 T120,20 T180,25 T240,55 L240,70 L0,70 Z"
                fill="url(#grad-viewers)"
              ></path>
              <circle className="text-primary animate-ping" cx="240" cy="55" fill="currentColor" r="3"></circle>
            </svg>
          </div>
          <div className="flex items-center justify-between font-code-xs text-code-xs text-outline">
            <span>13:30</span>
            <span>14:00</span>
            <span className="text-error font-medium">14:22 (Exits spike)</span>
          </div>
        </div>

        {/* Chart 2: DRM License Latency */}
        <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between gap-space-md shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">
                DRM Latency (ms)
              </span>
              <span className="font-metric-md text-metric-md text-primary font-bold">
                {drmLatencyStr} <span className="font-body-xs text-body-xs font-normal text-error">↑ +5,180%</span>
              </span>
            </div>
            <span className="material-symbols-outlined text-primary text-[18px]">key</span>
          </div>
          {/* Latency Spike Chart */}
          <div className="h-24 w-full flex items-end">
            <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 240 70">
              <defs>
                <linearGradient id="grad-drm" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#f97316" stopOpacity="0.4"></stop>
                  <stop offset="100%" stopColor="#f97316" stopOpacity="0.0"></stop>
                </linearGradient>
              </defs>
              <path
                className="text-primary-container"
                d="M0,64 L120,63 L140,60 L160,10 L240,8"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
              ></path>
              <path
                d="M0,64 L120,63 L140,60 L160,10 L240,8 L240,70 L0,70 Z"
                fill="url(#grad-drm)"
              ></path>
              <circle className="text-primary-container animate-pulse" cx="240" cy="8" fill="currentColor" r="3"></circle>
            </svg>
          </div>
          <div className="flex items-center justify-between font-code-xs text-code-xs text-outline">
            <span>Base: 35ms</span>
            <span className="text-error font-semibold">14:15 Degradation</span>
            <span>p99: 2,140ms</span>
          </div>
        </div>

        {/* Chart 3: Playback Failure Rate */}
        <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between gap-space-md shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">
                Playback Failure (%)
              </span>
              <span className="font-metric-md text-metric-md text-error font-bold">
                {playbackFailureStr} <span className="font-body-xs text-body-xs font-normal text-error">↑ Severe</span>
              </span>
            </div>
            <span className="material-symbols-outlined text-error text-[18px]">error</span>
          </div>
          {/* Playback Failure Chart */}
          <div className="h-24 w-full flex items-end">
            <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 240 70">
              <defs>
                <linearGradient id="grad-fail" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#ffb4ab" stopOpacity="0.5"></stop>
                  <stop offset="100%" stopColor="#ffb4ab" stopOpacity="0.0"></stop>
                </linearGradient>
              </defs>
              <path
                className="text-error"
                d="M0,66 L120,66 L145,55 L170,22 L240,14"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
              ></path>
              <path
                d="M0,66 L120,66 L145,55 L170,22 L240,14 L240,70 L0,70 Z"
                fill="url(#grad-fail)"
              ></path>
              <circle className="text-error animate-ping" cx="240" cy="14" fill="currentColor" r="3"></circle>
            </svg>
          </div>
          <div className="flex items-center justify-between font-code-xs text-code-xs text-outline">
            <span>SLA: 1.2%</span>
            <span className="text-error font-semibold">ExoPlayer Crash</span>
            <span>Current: {playbackFailureStr}</span>
          </div>
        </div>

        {/* Chart 4: CDN Hit Ratio & Gateway 5xx */}
        <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between gap-space-md shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">
                CDN Cache vs HTTP 504
              </span>
              <span className="font-metric-md text-metric-md text-on-surface font-bold">
                {cdnCacheStr} <span className="font-body-xs text-body-xs font-normal text-error">504: {http504Str}</span>
              </span>
            </div>
            <span className="material-symbols-outlined text-tertiary text-[18px]">dns</span>
          </div>
          {/* Dual Micro Chart */}
          <div className="h-24 w-full flex items-end">
            <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 240 70">
              <path
                className="text-secondary"
                d="M0,15 L60,14 L120,16 L180,15 L240,17"
                fill="none"
                stroke="currentColor"
                strokeDasharray="3 3"
                strokeWidth="1.5"
              ></path>
              <path
                className="text-primary-container"
                d="M0,68 L140,68 L170,40 L240,28"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              ></path>
            </svg>
          </div>
          <div className="flex items-center justify-between font-code-xs text-code-xs text-outline">
            <span className="text-secondary font-medium">-- Cache Nominal</span>
            <span className="text-primary font-medium">— 504 Timeouts</span>
          </div>
        </div>
      </div>
    </div>
  );
};
