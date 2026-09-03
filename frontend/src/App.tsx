import React, { useEffect, useState } from "react";
import { api } from "./api/client";
import type {
  HealthStatus,
  ScenarioSummary,
  InvestigationResponse,
  SimulationActionResponse,
} from "./api/client";

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [currentScenarioId, setCurrentScenarioId] = useState<string>("regional_streaming_incident");
  const [investigation, setInvestigation] = useState<InvestigationResponse | null>(null);
  const [isInvestigating, setIsInvestigating] = useState<boolean>(false);
  const [simulationModalOpen, setSimulationModalOpen] = useState<boolean>(false);
  const [simulationResult, setSimulationResult] = useState<SimulationActionResponse | null>(null);
  const [toast, setToast] = useState<{ title: string; subtitle: string } | null>(null);
  const [activeTab, setActiveTab] = useState<string>("overview");

  // Grafana Query State
  const [grafanaQueryType, setGrafanaQueryType] = useState<"prometheus" | "loki">("prometheus");
  const [grafanaQuery, setGrafanaQuery] = useState<string>("sum(rate(http_requests_total[5m]))");
  const [grafanaResult, setGrafanaResult] = useState<string | null>(null);
  const [isQueryingGrafana, setIsQueryingGrafana] = useState<boolean>(false);

  // Initial Load
  useEffect(() => {
    loadHealth();
    loadScenarios();
    runInvestigation("regional_streaming_incident");
  }, []);

  const loadHealth = async () => {
    try {
      const h = await api.getHealth();
      setHealth(h);
    } catch (e) {
      console.error("Health check failed:", e);
    }
  };

  const loadScenarios = async () => {
    try {
      const s = await api.getScenarios();
      setScenarios(s);
    } catch (e) {
      console.error("Failed to load scenarios:", e);
    }
  };

  const runInvestigation = async (scenarioId: string) => {
    setIsInvestigating(true);
    setCurrentScenarioId(scenarioId);
    try {
      const res = await api.investigateScenario(scenarioId);
      setInvestigation(res);
      await loadHealth();
    } catch (e) {
      console.error("Investigation error:", e);
    } finally {
      setIsInvestigating(false);
    }
  };

  const handleSimulateAction = async () => {
    try {
      const sim = await api.simulateAction(currentScenarioId, "drm_failover");
      setSimulationResult(sim);
      setSimulationModalOpen(true);
    } catch (e) {
      console.error("Simulation error:", e);
    }
  };

  const handleApplySimulatedRemediation = () => {
    setSimulationModalOpen(false);
    setToast({
      title: "Simulated Action Recorded",
      subtitle: simulationResult?.action || "No production infrastructure was modified (Simulation Only).",
    });
    setTimeout(() => setToast(null), 5000);
  };

  const handleRunGrafanaQuery = async () => {
    setIsQueryingGrafana(true);
    try {
      const res = await api.queryMCP(grafanaQueryType, grafanaQuery, "5m");
      setGrafanaResult(JSON.stringify(res, null, 2));
    } catch (e: any) {
      setGrafanaResult(`Error: ${e.message}`);
    } finally {
      setIsQueryingGrafana(false);
    }
  };

  const report = investigation?.report;
  const qoe = investigation?.aggregate_qoe;
  const release = investigation?.release_context;
  const isCritical = report?.classification === "CRITICAL_STREAMING_INCIDENT";

  return (
    <div className="bg-background font-body-sm text-body-sm text-on-surface antialiased min-h-screen">
      {/* 0. SIMULATION MODAL (Strictly Marked [SIMULATED]) */}
      {simulationModalOpen && simulationResult && (
        <div className="fixed inset-0 z-50 bg-surface-container-lowest/80 backdrop-blur-md flex items-center justify-center p-space-lg">
          <div className="bg-surface-container w-full max-w-2xl rounded-xl p-space-xl shadow-2xl flex flex-col gap-space-lg border border-primary-container/30">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-space-sm">
                <span className="w-3 h-3 rounded-full bg-primary-container animate-ping"></span>
                <span className="font-headline-md text-headline-md text-on-surface">
                  Operational Remediation Simulation [SIMULATED ACTION]
                </span>
              </div>
              <button
                className="p-space-xs text-on-surface-variant hover:text-on-surface rounded"
                onClick={() => setSimulationModalOpen(false)}
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            <div className="p-space-md bg-surface-container-lowest rounded-lg font-code-xs text-code-xs text-on-surface flex flex-col gap-space-xs border border-surface-container-high">
              <div className="text-tertiary">[POSTWIRE SIMULATOR] Evaluating mitigation strategy:</div>
              <div className="text-primary font-semibold">&gt; Action: {simulationResult.action}</div>
              <div className="text-on-surface-variant">&gt; Target cluster: {simulationResult.target_cluster}</div>
              <div className="text-on-surface-variant">&gt; Projected latency: {simulationResult.projected_ttfb}</div>
              <div className="text-primary">&gt; Projected failure reduction: {simulationResult.projected_playback_failure_reduction}</div>
              <div className="text-emerald-400 font-bold">&gt; SAFETY CHECK: {simulationResult.safety_check}</div>
              <div className="text-error font-bold mt-1">&gt; STATUS: {simulationResult.status} (Executed: {simulationResult.executed ? "TRUE" : "FALSE"})</div>
              <div className="text-outline italic">&gt; {simulationResult.message}</div>
            </div>

            <div className="flex items-center justify-end gap-space-md">
              <button
                className="px-space-lg py-space-xs bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-headline-sm text-headline-sm rounded"
                onClick={() => setSimulationModalOpen(false)}
              >
                Cancel
              </button>
              <button
                className="px-space-lg py-space-xs bg-primary-container hover:bg-primary-container/90 text-on-primary-container font-headline-sm text-headline-sm font-bold rounded shadow-lg flex items-center gap-space-xs"
                onClick={handleApplySimulatedRemediation}
              >
                <span className="material-symbols-outlined text-[16px]">play_arrow</span>
                Confirm Simulated Authorization
              </button>
            </div>
          </div>
        </div>
      )}

      {/* NOTIFICATION TOAST */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 bg-secondary-container text-on-secondary-container px-space-xl py-space-md rounded-lg shadow-2xl flex items-center gap-space-md transition-all duration-300 border border-secondary/40">
          <span className="material-symbols-outlined text-tertiary text-[22px]">check_circle</span>
          <div className="flex flex-col">
            <span className="font-headline-sm text-headline-sm font-bold text-on-surface">{toast.title}</span>
            <span className="font-body-xs text-body-xs text-on-surface-variant">{toast.subtitle}</span>
          </div>
        </div>
      )}

      {/* 1. TOP APP HEADER */}
      <header className="fixed top-0 left-0 right-0 h-16 z-50 bg-surface-container-lowest/90 backdrop-blur-xl border-b border-surface-container-high">
        <div className="h-16 w-full px-space-xl flex items-center justify-between gap-space-lg">
          <div className="flex items-center gap-space-lg">
            <div className="flex items-center gap-space-md">
              {/* Logo SVG */}
              <div className="w-8 h-8 rounded bg-primary-container/20 border border-primary-container flex items-center justify-center text-primary font-black text-sm">
                PW
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-space-sm">
                  <span className="font-headline-lg text-headline-lg font-bold tracking-tight text-on-background">
                    PostWire
                  </span>
                  <span className="px-space-xs py-space-2xs bg-surface-container-high rounded text-primary-fixed-dim font-label-caps text-label-caps uppercase border border-outline-variant/30">
                    AUTONOMOUS INCIDENT COMMANDER
                  </span>
                </div>
                <div className="flex items-center gap-space-xs mt-space-2xs">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary-container animate-pulse"></span>
                  <span className="font-code-xs text-code-xs text-on-surface-variant">
                    LIVE RELEASE: {release?.title || "Neon Tokyo: Origins"} ({release?.release_id || "rel_neontokyo_2026"})
                  </span>
                </div>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="hidden xl:flex items-center gap-space-xs ml-space-xl">
              {[
                { id: "overview", label: "Overview" },
                { id: "incidents", label: "Incidents", badge: isCritical ? "1 CRITICAL" : "0 FAULTS" },
                { id: "releases", label: "Releases" },
                { id: "viewer-qoe", label: "Viewer QoE" },
                { id: "grafana", label: "Grafana MCP" },
                { id: "investigation-history", label: "Investigation History" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-space-md py-space-xs font-body-sm transition-colors flex items-center gap-space-xs rounded ${
                    activeTab === tab.id
                      ? "bg-surface-container-high text-primary-fixed border border-outline-variant/40"
                      : "text-on-surface-variant hover:text-on-surface"
                  }`}
                >
                  <span>{tab.label}</span>
                  {tab.badge && (
                    <span
                      className={`px-space-xs py-space-2xs font-label-caps text-label-caps rounded-full ${
                        isCritical
                          ? "bg-error-container/80 text-error"
                          : "bg-secondary-container/80 text-secondary"
                      }`}
                    >
                      {tab.badge}
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>

          {/* Right Status Indicators & Demo Controls */}
          <div className="flex items-center gap-space-md">
            <div className="hidden md:flex items-center gap-space-sm font-code-xs text-code-xs">
              {/* Scenario Selector */}
              <div className="flex items-center bg-surface-container-high/60 rounded p-0.5 border border-surface-container-high">
                {(scenarios.length > 0 ? scenarios : [
                  { id: "regional_streaming_incident", name: "Regional Incident (APAC)", description: "", release_title: "", expected_classification: "CRITICAL_STREAMING_INCIDENT" },
                  { id: "normal_movie_premiere", name: "Normal Premiere (8× Surge)", description: "", release_title: "", expected_classification: "EXPECTED_PREMIERE_SURGE" },
                ]).map((scen) => (
                  <button
                    key={scen.id}
                    onClick={() => runInvestigation(scen.id)}
                    disabled={isInvestigating}
                    className={`px-space-sm py-space-2xs rounded font-semibold transition-all ${
                      currentScenarioId === scen.id
                        ? scen.id === "regional_streaming_incident"
                          ? "bg-error-container text-error shadow"
                          : "bg-secondary-container text-secondary shadow"
                        : "text-on-surface-variant hover:text-on-surface"
                    }`}
                  >
                    {scen.id === "regional_streaming_incident" ? "Regional Incident (APAC)" : "Normal Premiere (8× Surge)"}
                  </button>
                ))}
              </div>

              {/* MCP Status */}
              <div className="flex items-center gap-space-xs px-space-sm py-space-2xs bg-surface-container rounded border border-surface-container-high">
                <span className="w-2 h-2 rounded-full bg-primary-container"></span>
                <span className="text-on-surface-variant">GRAFANA MCP:</span>
                <span className="text-primary font-semibold uppercase">{health?.grafana_mcp_active_mode || "LIVE"}</span>
              </div>

              {/* AI Runtime Status */}
              <div className="flex items-center gap-space-xs px-space-sm py-space-2xs bg-surface-container rounded border border-surface-container-high">
                <span className="w-2 h-2 rounded-full bg-tertiary-container animate-pulse"></span>
                <span className="text-on-surface-variant">COMMANDER:</span>
                <span className="text-tertiary font-semibold" title={report?.summary || ""}>
                  {health?.commander_ai_runtime?.includes("Google ADK") && !report?.summary.includes("Fallback")
                    ? "GOOGLE ADK + GEMINI"
                    : "SAFETY FALLBACK"}
                </span>
              </div>
            </div>

            {/* Manual Trigger Button */}
            <button
              onClick={() => runInvestigation(currentScenarioId)}
              disabled={isInvestigating}
              className="px-space-md py-space-xs bg-primary-container hover:bg-primary-container/90 text-on-primary-container font-headline-sm text-headline-sm font-bold rounded shadow flex items-center gap-space-2xs transition-all disabled:opacity-50"
            >
              <span className={`material-symbols-outlined text-[18px] ${isInvestigating ? "animate-spin" : ""}`}>
                {isInvestigating ? "autorenew" : "crisis_alert"}
              </span>
              <span>{isInvestigating ? "Investigating..." : "Re-Investigate"}</span>
            </button>
          </div>
        </div>
      </header>

      {/* 2. LEFT SIDEBAR */}
      <aside className="fixed left-0 top-16 bottom-0 w-14 bg-surface-container-lowest border-r border-surface-container-high z-40 flex flex-col justify-between items-center py-space-md">
        <div className="flex flex-col items-center gap-space-md">
          <button
            onClick={() => setActiveTab("overview")}
            className={`p-space-sm rounded transition-colors ${
              activeTab === "overview" ? "text-primary bg-surface-container-high" : "text-on-surface-variant hover:text-on-surface"
            }`}
            title="War Room Operations"
          >
            <span className="material-symbols-outlined text-[20px]">emergency_home</span>
          </button>
          <button
            onClick={() => setActiveTab("incidents")}
            className={`p-space-sm rounded transition-colors ${
              activeTab === "incidents" ? "text-primary bg-surface-container-high" : "text-on-surface-variant hover:text-on-surface"
            }`}
            title="Live Incident Stream"
          >
            <span className="material-symbols-outlined text-[20px]">warning</span>
          </button>
          <button
            onClick={() => setActiveTab("viewer-qoe")}
            className={`p-space-sm rounded transition-colors ${
              activeTab === "viewer-qoe" ? "text-primary bg-surface-container-high" : "text-on-surface-variant hover:text-on-surface"
            }`}
            title="Viewer QoE Matrix"
          >
            <span className="material-symbols-outlined text-[20px]">monitoring</span>
          </button>
          <button
            onClick={() => setActiveTab("grafana")}
            className={`p-space-sm rounded transition-colors ${
              activeTab === "grafana" ? "text-primary bg-surface-container-high" : "text-on-surface-variant hover:text-on-surface"
            }`}
            title="Grafana Observability"
          >
            <span className="material-symbols-outlined text-[20px]">troubleshoot</span>
          </button>
          <button
            onClick={() => setActiveTab("investigation-history")}
            className={`p-space-sm rounded transition-colors ${
              activeTab === "investigation-history" ? "text-primary bg-surface-container-high" : "text-on-surface-variant hover:text-on-surface"
            }`}
            title="Audit Logs"
          >
            <span className="material-symbols-outlined text-[20px]">history_toggle_off</span>
          </button>
        </div>
      </aside>

      {/* 3. MAIN DASHBOARD CONTENT */}
      <div className="pl-14 pt-16">
        <main className="p-space-lg xl:p-space-2xl flex flex-col gap-space-xl max-w-[1880px] mx-auto w-full">
          {/* HERO ALERT BANNER */}
          <div className="relative overflow-hidden rounded-xl bg-surface-container p-space-lg xl:p-space-xl shadow-xl flex flex-col gap-space-lg border border-surface-container-high">
            <div
              className={`absolute -right-24 -top-24 w-96 h-96 rounded-full blur-3xl pointer-events-none ${
                isCritical ? "bg-error-container/20" : "bg-secondary-container/20"
              }`}
            ></div>
            <div className="relative z-10 flex flex-col xl:flex-row xl:items-center justify-between gap-space-md">
              <div className="flex flex-wrap items-center gap-space-md">
                <div
                  className={`flex items-center gap-space-xs px-space-md py-space-xs rounded font-label-caps text-label-caps uppercase shadow-sm ${
                    isCritical ? "bg-error-container text-error animate-pulse" : "bg-secondary-container text-secondary"
                  }`}
                >
                  <span className="material-symbols-outlined text-[14px]">
                    {isCritical ? "crisis_alert" : "verified"}
                  </span>
                  <span>{report?.classification || "ANALYZING..."}</span>
                </div>
                <span className="font-headline-xl text-headline-xl font-bold tracking-tight text-on-surface">
                  {release?.title || "Movie Release Premiere"}
                </span>
                <div className="flex items-center gap-space-xs px-space-sm py-space-2xs bg-surface-container-high rounded text-on-surface-variant font-code-xs text-code-xs">
                  <span className="material-symbols-outlined text-[13px] text-outline">movie</span>
                  <span>ID: {release?.release_id || "rel_id"}</span>
                </div>
                <div className="flex items-center gap-space-xs px-space-sm py-space-2xs bg-surface-container-high rounded text-on-surface-variant font-code-xs text-code-xs">
                  <span className="material-symbols-outlined text-[13px] text-outline">schedule</span>
                  <span>Premiere: {release?.premiere_window_start ? new Date(release.premiere_window_start).toLocaleTimeString() : "Live"}</span>
                </div>
              </div>

              <div className="flex items-center gap-space-sm flex-wrap">
                <span className="px-space-sm py-space-xs bg-surface-container-lowest rounded font-code-sm text-code-sm text-primary font-bold">
                  {release?.expected_viewer_surge_factor || 1.0}× EXPECTED SURGE
                </span>
                <span className="px-space-sm py-space-xs bg-surface-container-lowest rounded font-label-caps text-label-caps text-tertiary">
                  {release?.marketing_tier || "GLOBAL PREMIERE"}
                </span>
                <div className="flex items-center gap-1">
                  {release?.high_value_devices?.map((d) => (
                    <span key={d} className="px-1.5 py-0.5 bg-surface-container-high rounded text-[10px] text-on-surface-variant font-mono">
                      {d}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Differentiated Callout Banner */}
            <div className="relative z-10 p-space-md bg-surface-container-lowest rounded-lg border border-surface-container-high flex flex-col sm:flex-row sm:items-center justify-between gap-space-md">
              <div className="flex items-start gap-space-sm">
                <span className={`material-symbols-outlined text-[20px] shrink-0 mt-0.5 ${isCritical ? "text-error" : "text-secondary"}`}>
                  {isCritical ? "report" : "check_circle"}
                </span>
                <div className="flex flex-col">
                  <span className="font-headline-sm text-headline-sm font-semibold text-on-surface">
                    {report?.summary || "Investigating streaming telemetry across edge points..."}
                  </span>
                  <span className="font-code-xs text-code-xs text-on-surface-variant mt-0.5">
                    Triggered by: {investigation?.alert_event || "System alert"}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-space-md shrink-0">
                <div className="flex flex-col items-end">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Decision Confidence</span>
                  <span className={`font-metric-md text-metric-md font-bold ${isCritical ? "text-error" : "text-secondary"}`}>
                    {report?.confidence ? `${Math.round(report.confidence * 100)}%` : "--"}
                  </span>
                </div>
              </div>
            </div>

            {/* High-Density Telemetry Metric Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-space-md">
              {/* Metric 1: Playback Failure */}
              <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between shadow-sm border border-surface-container-high">
                <div className="flex items-center justify-between">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Playback Failure</span>
                  <span className="px-space-xs py-space-2xs bg-surface-container-high text-on-surface rounded font-code-xs text-code-xs">
                    SLA: 1.2%
                  </span>
                </div>
                <div className="flex items-baseline justify-between mt-space-sm">
                  <span className={`font-metric-display text-metric-display font-bold tracking-tight ${isCritical ? "text-error" : "text-secondary"}`}>
                    {qoe ? `${(qoe.avg_playback_failure_rate * 100).toFixed(2)}%` : "--"}
                  </span>
                  <span className="font-code-xs text-code-xs text-on-surface-variant">
                    {isCritical ? "Elevated" : "Nominal"}
                  </span>
                </div>
                <div className="w-full bg-surface-container-highest h-1 rounded mt-space-sm overflow-hidden">
                  <div
                    className={`h-full rounded ${isCritical ? "bg-error" : "bg-secondary"}`}
                    style={{ width: `${Math.min(100, (qoe?.avg_playback_failure_rate || 0) * 500)}%` }}
                  ></div>
                </div>
              </div>

              {/* Metric 2: EBVS */}
              <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between shadow-sm border border-surface-container-high">
                <div className="flex items-center justify-between">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">EBVS (Exit Before Start)</span>
                  <span className="px-space-xs py-space-2xs bg-surface-container-high text-on-surface rounded font-code-xs text-code-xs">
                    Threshold &lt; 1%
                  </span>
                </div>
                <div className="flex items-baseline justify-between mt-space-sm">
                  <span className={`font-metric-display text-metric-display font-bold tracking-tight ${isCritical ? "text-error" : "text-secondary"}`}>
                    {qoe ? `${(qoe.avg_exit_before_video_start * 100).toFixed(2)}%` : "--"}
                  </span>
                  <span className="font-code-xs text-code-xs text-on-surface-variant">
                    {isCritical ? "Dropout" : "Healthy"}
                  </span>
                </div>
                <div className="w-full bg-surface-container-highest h-1 rounded mt-space-sm overflow-hidden">
                  <div
                    className={`h-full rounded ${isCritical ? "bg-error" : "bg-secondary"}`}
                    style={{ width: `${Math.min(100, (qoe?.avg_exit_before_video_start || 0) * 800)}%` }}
                  ></div>
                </div>
              </div>

              {/* Metric 3: DRM Latency */}
              <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between shadow-sm border border-surface-container-high">
                <div className="flex items-center justify-between">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">DRM License Latency</span>
                  <span className="px-space-xs py-space-2xs bg-surface-container-high text-primary rounded font-code-xs text-code-xs">
                    Base: 35ms
                  </span>
                </div>
                <div className="flex items-baseline justify-between mt-space-sm">
                  <span className="font-metric-display text-metric-display text-primary font-bold tracking-tight">
                    {qoe ? `${Math.round(qoe.avg_drm_license_latency_ms)} ms` : "--"}
                  </span>
                  <span className="font-code-xs text-code-xs text-primary font-medium">
                    {qoe && qoe.avg_drm_license_latency_ms > 100 ? "Spike" : "Normal"}
                  </span>
                </div>
                <div className="w-full bg-surface-container-highest h-1 rounded mt-space-sm overflow-hidden">
                  <div
                    className="bg-primary h-full rounded"
                    style={{ width: `${Math.min(100, ((qoe?.avg_drm_license_latency_ms || 35) / 1850) * 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Metric 4: Concurrent Viewers */}
              <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between shadow-sm border border-surface-container-high">
                <div className="flex items-center justify-between">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Concurrent Viewers</span>
                  <span className="px-space-xs py-space-2xs bg-surface-container-high text-tertiary rounded font-code-xs text-code-xs">
                    Live Stream
                  </span>
                </div>
                <div className="flex items-baseline justify-between mt-space-sm">
                  <span className="font-metric-display text-metric-display text-on-surface font-bold tracking-tight">
                    {qoe ? `${(qoe.total_concurrent_viewers / 1_000_000).toFixed(2)}M` : "--"}
                  </span>
                  <span className="font-code-xs text-code-xs text-tertiary font-medium">
                    {qoe?.total_request_rate_rps ? `${Math.round(qoe.total_request_rate_rps).toLocaleString()} rps` : "--"}
                  </span>
                </div>
                <div className="w-full bg-surface-container-highest h-1 rounded mt-space-sm overflow-hidden">
                  <div className="bg-tertiary h-full rounded" style={{ width: "65%" }}></div>
                </div>
              </div>

              {/* Metric 5: Viewer Impact Score */}
              <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between shadow-sm border border-surface-container-high">
                <div className="flex items-center justify-between">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Viewer Impact Score</span>
                  <span
                    className={`px-space-xs py-space-2xs rounded font-code-xs text-code-xs ${
                      isCritical ? "bg-error-container text-error" : "bg-secondary-container text-secondary"
                    }`}
                  >
                    VIS: 0–100
                  </span>
                </div>
                <div className="flex items-baseline justify-between mt-space-sm">
                  <span className={`font-metric-display text-metric-display font-bold tracking-tight ${isCritical ? "text-error" : "text-secondary"}`}>
                    {qoe ? qoe.viewer_impact_score.toFixed(1) : "--"}
                  </span>
                  <span className="font-code-xs text-code-xs text-on-surface-variant">
                    {isCritical ? "Severe" : "Healthy"}
                  </span>
                </div>
                <div className="w-full bg-surface-container-highest h-1 rounded mt-space-sm overflow-hidden">
                  <div
                    className={`h-full rounded ${isCritical ? "bg-error" : "bg-secondary"}`}
                    style={{ width: `${Math.min(100, qoe?.viewer_impact_score || 0)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* 4. CORE COMMAND ROW: INVESTIGATION VS DECISION/MITIGATION */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
            {/* COLUMN A: COMMANDER INVESTIGATION STREAM (7 Cols) */}
            <div className="lg:col-span-7 bg-surface-container rounded-xl p-space-lg flex flex-col gap-space-md shadow-lg border border-surface-container-high">
              <div className="flex items-center justify-between flex-wrap gap-space-sm">
                <div className="flex items-center gap-space-sm">
                  <div className="w-7 h-7 rounded bg-secondary-container flex items-center justify-center">
                    <span className="material-symbols-outlined text-secondary text-[18px]">psychology</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="font-headline-md text-headline-md font-bold text-on-surface">
                      Autonomous Investigation Stream
                    </span>
                    <span className="font-body-xs text-body-xs text-tertiary flex items-center gap-space-2xs">
                      <span className="w-1.5 h-1.5 rounded-full bg-tertiary animate-ping"></span>
                      Powered by {health?.gemini_model || "Gemini"} &amp; Google ADK
                    </span>
                  </div>
                </div>
                <span className="px-space-sm py-space-2xs bg-surface-container-lowest text-on-surface-variant rounded font-label-caps text-label-caps">
                  {report?.investigation_steps?.length || 0} TRACES RECORDED
                </span>
              </div>

              {/* Chronological Investigation Steps */}
              <div className="flex flex-col gap-space-xs mt-space-xs">
                {report?.investigation_steps?.map((step) => (
                  <div
                    key={step.step_number}
                    className="p-space-sm bg-surface-container-lowest rounded-lg flex items-start gap-space-md transition-colors hover:bg-surface-container-high/60 border border-surface-container-high/50"
                  >
                    <span className="font-code-xs text-code-xs text-outline shrink-0 mt-0.5">
                      STEP #{step.step_number}
                    </span>
                    <span className="material-symbols-outlined text-secondary text-[16px] shrink-0 mt-0.5">verified</span>
                    <div className="flex flex-col gap-space-2xs w-full min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="font-label-caps text-label-caps text-tertiary font-bold uppercase">
                          TOOL: {step.tool_used}
                        </span>
                        <span className="font-code-xs text-code-xs text-secondary-fixed-dim">COMPLETED</span>
                      </div>
                      <p className="font-body-xs text-body-xs text-on-surface">
                        <span className="font-semibold text-on-surface-variant">{step.query_summary}</span> — {step.evidence_discovered}
                      </p>
                    </div>
                  </div>
                ))}
                {(!report?.investigation_steps || report.investigation_steps.length === 0) && (
                  <div className="p-space-md text-center text-on-surface-variant">No investigation steps recorded yet.</div>
                )}
              </div>

              <div className="p-space-sm bg-surface-container-high/50 rounded flex items-center justify-between text-on-surface-variant font-code-xs text-code-xs">
                <span className="flex items-center gap-space-xs">
                  <span className="material-symbols-outlined text-tertiary text-[14px]">info</span>
                  Correlated without chain-of-thought exposure (concise operational evidence only).
                </span>
                <span className="text-tertiary font-medium">INCIDENT_ID: {report?.incident_id || "--"}</span>
              </div>
            </div>

            {/* COLUMN B: INCIDENT DECISION & RECOMMENDED MITIGATION (5 Cols) */}
            <div className="lg:col-span-5 flex flex-col gap-space-md">
              {/* Decision Card */}
              <div className="bg-surface-container rounded-xl p-space-lg flex flex-col gap-space-md shadow-lg relative overflow-hidden border border-surface-container-high">
                <div className="flex items-center justify-between">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Incident Classification</span>
                  <div
                    className={`flex items-center gap-space-xs px-space-sm py-space-2xs rounded-full font-label-caps text-label-caps shadow-sm ${
                      isCritical ? "bg-error-container text-error" : "bg-secondary-container text-secondary"
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-current animate-ping"></span>
                    <span>{report?.confidence ? `${Math.round(report.confidence * 100)}% CONFIDENCE` : "--"}</span>
                  </div>
                </div>

                <div className="flex items-baseline gap-space-sm">
                  <span className={`font-headline-lg text-headline-lg font-bold ${isCritical ? "text-error" : "text-secondary"}`}>
                    {report?.classification || "ANALYZING"}
                  </span>
                </div>

                <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col gap-space-xs border border-surface-container-high">
                  <span className="font-label-caps text-label-caps text-tertiary uppercase">Reason Summary</span>
                  <p className="font-body-sm text-body-sm text-on-surface italic">
                    "{report?.summary || "Awaiting evaluation..."}"
                  </p>
                </div>

                <div className="flex items-center justify-between p-space-sm bg-surface-container-lowest rounded-lg border border-surface-container-high">
                  <div className="flex items-center gap-space-sm">
                    <span className="material-symbols-outlined text-error text-[20px]">people_alt</span>
                    <div className="flex flex-col">
                      <span className="font-label-caps text-label-caps text-on-surface-variant">AFFECTED REGION &amp; DEVICE</span>
                      <span className="font-metric-md text-metric-md text-on-surface font-bold">
                        {report?.affected_region || "None"} • {report?.affected_device || "All"}
                      </span>
                    </div>
                  </div>
                  <span className="px-space-sm py-space-2xs bg-surface-container text-outline rounded font-code-xs text-code-xs">
                    {report?.affected_region || "Global"}
                  </span>
                </div>
              </div>

              {/* Recommended Mitigation Card */}
              <div className="bg-surface-container rounded-xl p-space-lg flex flex-col gap-space-md shadow-lg border border-surface-container-high">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-space-xs">
                    <span className="material-symbols-outlined text-primary-container text-[18px]">build</span>
                    <span className="font-headline-md text-headline-md font-bold text-on-surface">Recommended Mitigation</span>
                  </div>
                  <span className="px-space-xs py-space-2xs bg-primary-container/20 text-primary-container font-label-caps text-label-caps rounded">
                    SIMULATED ACTIONS READY
                  </span>
                </div>

                <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col gap-space-xs border border-surface-container-high">
                  <div className="flex items-center gap-space-xs font-label-caps text-label-caps text-primary">
                    <span className="material-symbols-outlined text-[14px]">alt_route</span>
                    <span>ACTION PROPOSAL</span>
                  </div>
                  <p className="font-body-sm text-body-sm font-semibold text-on-surface">
                    {report?.recommended_mitigation || "No action required for nominal surge."}
                  </p>
                  <span className="font-body-xs text-body-xs text-on-surface-variant mt-space-2xs">
                    Advisory Mode: Operator authorization is required before applying simulated changes.
                  </span>
                </div>

                {/* Simulation Action Buttons */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-space-sm mt-space-xs">
                  <button
                    onClick={handleSimulateAction}
                    className="px-space-md py-space-sm bg-primary-container hover:bg-primary-container/90 text-on-primary-container font-headline-sm text-headline-sm font-bold rounded shadow flex items-center justify-center gap-space-2xs transition-all"
                  >
                    <span className="material-symbols-outlined text-[16px]">terminal</span>
                    <span>Simulate Action</span>
                  </button>
                  <button
                    onClick={() => {
                      setToast({
                        title: "Audit Log Exported",
                        subtitle: `Post-Mortem for ${report?.incident_id || "incident"} saved to local store.`,
                      });
                      setTimeout(() => setToast(null), 4000);
                    }}
                    className="px-space-md py-space-sm bg-surface-container-high hover:bg-surface-bright text-on-surface font-headline-sm text-headline-sm font-medium rounded flex items-center justify-center gap-space-2xs transition-all"
                  >
                    <span className="material-symbols-outlined text-[16px]">campaign</span>
                    <span>Status Post</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* 5. REAL-TIME GRAFANA OBSERVABILITY SECTION */}
          <div className="bg-surface-container rounded-xl p-space-lg flex flex-col gap-space-lg shadow-lg border border-surface-container-high">
            <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-space-md">
              <div className="flex items-center gap-space-sm">
                <div className="w-7 h-7 rounded bg-surface-container-high flex items-center justify-center">
                  <span className="material-symbols-outlined text-primary-container text-[18px]">show_chart</span>
                </div>
                <div className="flex flex-col">
                  <div className="flex items-center gap-space-xs">
                    <span className="font-headline-md text-headline-md font-bold text-on-surface">
                      Grafana Cloud Observability &amp; MCP Telemetry
                    </span>
                    <span className="px-space-xs py-space-2xs bg-surface-container-lowest text-tertiary rounded font-label-caps text-label-caps">
                      OFFICIAL MCP-GRAFANA v1.3.0
                    </span>
                  </div>
                  <span className="font-body-xs text-body-xs text-on-surface-variant">
                    Connected to {health?.environment === "production" ? "Grafana Cloud" : "https://nimbleelk3407.grafana.net"} via stdio JSON-RPC
                  </span>
                </div>
              </div>

              {/* Interactive MCP Query Toolbar */}
              <div className="flex items-center gap-space-xs flex-wrap">
                <select
                  value={grafanaQueryType}
                  onChange={(e) => {
                    const t = e.target.value as "prometheus" | "loki";
                    setGrafanaQueryType(t);
                    setGrafanaQuery(t === "prometheus" ? "sum(rate(http_requests_total[5m]))" : '{app="drm"} |= "error"');
                  }}
                  className="bg-surface-container-lowest px-space-sm py-space-xs rounded text-body-xs text-on-surface border border-surface-container-high"
                >
                  <option value="prometheus">Prometheus PromQL</option>
                  <option value="loki">Loki LogQL</option>
                </select>
                <input
                  type="text"
                  value={grafanaQuery}
                  onChange={(e) => setGrafanaQuery(e.target.value)}
                  className="bg-surface-container-lowest px-space-md py-space-xs rounded text-code-xs font-mono text-on-surface w-80 border border-surface-container-high focus:outline-none focus:border-primary"
                  placeholder="Enter query..."
                />
                <button
                  onClick={handleRunGrafanaQuery}
                  disabled={isQueryingGrafana}
                  className="px-space-md py-space-xs bg-surface-container-high hover:bg-surface-bright rounded text-body-xs font-semibold text-on-surface transition-colors flex items-center gap-1"
                >
                  <span className={`material-symbols-outlined text-[14px] ${isQueryingGrafana ? "animate-spin" : ""}`}>
                    {isQueryingGrafana ? "autorenew" : "play_arrow"}
                  </span>
                  <span>{isQueryingGrafana ? "Querying..." : "Run MCP"}</span>
                </button>
              </div>
            </div>

            {/* MCP Query Output Console (if run) */}
            {grafanaResult && (
              <div className="p-space-md bg-surface-container-lowest rounded-lg border border-surface-container-high font-mono text-xs overflow-x-auto max-h-48 text-primary-fixed-dim">
                <pre>{grafanaResult}</pre>
              </div>
            )}

            {/* Observability Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-space-md">
              <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between gap-space-md shadow-sm border border-surface-container-high">
                <div className="flex items-center justify-between">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">DRM Duration (p99)</span>
                  <span className="material-symbols-outlined text-primary text-[18px]">key</span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className="font-metric-md text-metric-md text-primary font-bold">
                    {qoe?.avg_drm_license_latency_ms ? `${Math.round(qoe.avg_drm_license_latency_ms)} ms` : "35 ms"}
                  </span>
                  <span className="font-code-xs text-code-xs text-on-surface-variant">PromQL Metric</span>
                </div>
                <div className="text-[11px] text-outline font-mono">rate(drm_license_duration_ms[5m])</div>
              </div>

              <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between gap-space-md shadow-sm border border-surface-container-high">
                <div className="flex items-center justify-between">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">CDN Cache Hit Ratio</span>
                  <span className="material-symbols-outlined text-tertiary text-[18px]">dns</span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className="font-metric-md text-metric-md text-on-surface font-bold">
                    {qoe ? `${(qoe.avg_cdn_cache_hit_ratio * 100).toFixed(1)}%` : "98.2%"}
                  </span>
                  <span className="font-code-xs text-code-xs text-secondary font-medium">Edge Healthy</span>
                </div>
                <div className="text-[11px] text-outline font-mono">sum(cdn_cache_hits) / sum(cdn_requests)</div>
              </div>

              <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between gap-space-md shadow-sm border border-surface-container-high">
                <div className="flex items-center justify-between">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Manifest Fetch Latency</span>
                  <span className="material-symbols-outlined text-secondary text-[18px]">timer</span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className="font-metric-md text-metric-md text-on-surface font-bold">
                    {qoe ? `${qoe.avg_manifest_latency_ms.toFixed(1)} ms` : "24 ms"}
                  </span>
                  <span className="font-code-xs text-code-xs text-secondary font-medium">HLS / DASH OK</span>
                </div>
                <div className="text-[11px] text-outline font-mono">histogram_quantile(0.95, manifest_ms)</div>
              </div>

              <div className="p-space-md bg-surface-container-lowest rounded-lg flex flex-col justify-between gap-space-md shadow-sm border border-surface-container-high">
                <div className="flex items-center justify-between">
                  <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Active Grafana Alerts</span>
                  <span className="material-symbols-outlined text-error text-[18px]">crisis_alert</span>
                </div>
                <div className="flex items-baseline justify-between">
                  <span className={`font-metric-md text-metric-md font-bold ${isCritical ? "text-error" : "text-secondary"}`}>
                    {isCritical ? "1 Firing Rule" : "0 Firing (Normal)"}
                  </span>
                  <span className="font-code-xs text-code-xs text-outline">Grafana Alerting</span>
                </div>
                <div className="text-[11px] text-outline font-mono">alerting_manage_rules / groups</div>
              </div>
            </div>
          </div>

          {/* 6. REGIONAL IMPACT MATRIX TABLE */}
          <div className="bg-surface-container rounded-xl p-space-lg flex flex-col gap-space-md shadow-lg overflow-x-auto border border-surface-container-high">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-space-xs">
                <span className="material-symbols-outlined text-outline text-[18px]">public</span>
                <span className="font-headline-md text-headline-md font-bold text-on-surface">Regional Impact Matrix</span>
              </div>
              <span className="font-code-xs text-code-xs text-on-surface-variant">5 Edge Delivery Regions</span>
            </div>

            <table className="w-full text-left font-body-sm text-body-sm">
              <thead>
                <tr className="text-on-surface-variant font-label-caps text-label-caps uppercase bg-surface-container-lowest/70 rounded">
                  <th className="py-space-sm px-space-md">Edge Region</th>
                  <th className="py-space-sm px-space-md">Impact Score (VIS)</th>
                  <th className="py-space-sm px-space-md">Playback Failures</th>
                  <th className="py-space-sm px-space-md">DRM Latency</th>
                  <th className="py-space-sm px-space-md">Rebuffer Ratio</th>
                  <th className="py-space-sm px-space-md text-right">Cluster Status</th>
                </tr>
              </thead>
              <tbody className="divide-y-0">
                {investigation?.regional_breakdown?.map((reg) => {
                  const regCritical = reg.status === "CRITICAL";
                  return (
                    <tr
                      key={reg.region}
                      className={`transition-colors ${
                        regCritical ? "bg-error-container/15 hover:bg-error-container/25" : "hover:bg-surface-container-high/40"
                      }`}
                    >
                      <td className="py-space-sm px-space-md font-semibold text-on-surface flex items-center gap-space-xs">
                        {regCritical && <span className="w-2 h-2 rounded-full bg-error animate-ping"></span>}
                        <span>{reg.region}</span>
                      </td>
                      <td className={`py-space-sm px-space-md font-code-sm text-code-sm font-bold ${regCritical ? "text-error" : "text-secondary"}`}>
                        {reg.viewer_impact_score} / 100
                      </td>
                      <td className={`py-space-sm px-space-md font-code-sm text-code-sm font-bold ${regCritical ? "text-error" : "text-secondary"}`}>
                        {(reg.playback_failure_rate * 100).toFixed(2)}%
                      </td>
                      <td className={`py-space-sm px-space-md font-code-sm text-code-sm font-bold ${regCritical ? "text-primary" : "text-on-surface-variant"}`}>
                        {Math.round(reg.drm_license_latency_ms)} ms
                      </td>
                      <td className="py-space-sm px-space-md font-code-sm text-code-sm text-on-surface">
                        {(reg.rebuffer_ratio * 100).toFixed(2)}%
                      </td>
                      <td className="py-space-sm px-space-md text-right">
                        <span
                          className={`px-space-xs py-space-2xs rounded font-label-caps text-label-caps font-bold ${
                            regCritical ? "bg-error-container text-error" : "bg-secondary-container/30 text-secondary"
                          }`}
                        >
                          {regCritical ? "CRITICAL" : "HEALTHY"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
