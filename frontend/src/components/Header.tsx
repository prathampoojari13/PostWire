import React from "react";
import type { HealthStatus, MovieReleaseContext, IncidentReport } from "../api/client";

interface HeaderProps {
  health: HealthStatus | null;
  releaseContext: MovieReleaseContext | null;
  report: IncidentReport | null;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  currentScenario: string;
  onSwitchScenario: (scenarioId: string) => void;
  isInvestigating: boolean;
  onReInvestigate: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  releaseContext,
  report,
  activeTab,
  setActiveTab,
  currentScenario,
  onSwitchScenario,
  isInvestigating,
  onReInvestigate,
}) => {
  const isCritical = report?.classification === "CRITICAL_STREAMING_INCIDENT";

  return (
    <header className="fixed top-0 left-0 right-0 h-16 z-50 bg-surface-container-lowest/90 backdrop-blur-xl border-b border-surface-container-high">
      <div className="h-16 w-full px-space-xl flex items-center justify-between gap-space-lg">
        <div className="flex items-center gap-space-lg">
          <div className="flex items-center gap-space-md">
            <img
              alt="PostWire Logo"
              className="h-8 w-auto object-contain"
              src="https://lh3.googleusercontent.com/aida/AEtjO1Uu13m0R4VEUB-R1rNWgy1V0Si-LJopvvNCRONEoUdRbiTapAcsMLduc0zbBpunL0lSDG8KqAenUq9lEiwKZebe1qjWaBcRXPd3WFkpJuw7CuPyfCxd98MOYe7aPNDzwHgpm-DBWwBmaCrKhTOow0tW_LvcUzO0wcwG5S7VgiI9XIaWRY0BpGqLfWU85X2xZMSslSDkUAzmN0Df0yBuUvwY1W4o-QASBPCAUZW2M-iGGtS1ZpwF2BicvzSf"
            />
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
                  LIVE RELEASE: {releaseContext ? releaseContext.title : "Neon Tokyo: Origins"}
                </span>
              </div>
            </div>
          </div>

          <nav className="hidden xl:flex items-center gap-space-xs ml-space-xl">
            {[
              { id: "overview", label: "Overview" },
              {
                id: "incidents",
                label: "Incidents",
                badge: isCritical ? "1 CRITICAL" : "0 FAULTS",
                isError: isCritical,
              },
              { id: "releases", label: "Releases" },
              { id: "viewer-qoe", label: "Viewer QoE" },
              { id: "grafana", label: "Grafana" },
              { id: "investigation-history", label: "Investigation History" },
            ].map((tab) => {
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-space-md py-space-xs font-body-sm transition-colors flex items-center gap-space-xs ${
                    active
                      ? "bg-surface-container-high text-primary-fixed border border-outline-variant/40 rounded"
                      : "text-body-sm text-on-surface-variant hover:text-on-surface"
                  }`}
                >
                  <span>{tab.label}</span>
                  {tab.badge && (
                    <span
                      className={`px-space-xs py-space-2xs font-label-caps text-label-caps rounded-full ${
                        tab.isError ? "bg-error-container/80 text-error" : "bg-surface-container-highest text-secondary"
                      }`}
                    >
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center gap-space-md">
          {/* Scenario Switching Toolbar */}
          <div className="flex items-center bg-surface-container-high/60 rounded p-0.5 border border-surface-container-high font-code-xs text-code-xs">
            <button
              onClick={() => onSwitchScenario("regional_streaming_incident")}
              disabled={isInvestigating}
              className={`px-space-sm py-space-2xs rounded font-semibold transition-all ${
                currentScenario === "regional_streaming_incident"
                  ? "bg-error-container text-error shadow"
                  : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              Regional Incident (APAC)
            </button>
            <button
              onClick={() => onSwitchScenario("normal_movie_premiere")}
              disabled={isInvestigating}
              className={`px-space-sm py-space-2xs rounded font-semibold transition-all ${
                currentScenario === "normal_movie_premiere"
                  ? "bg-secondary-container text-secondary shadow"
                  : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              Normal Premiere (8× Surge)
            </button>
          </div>

          <div className="hidden md:flex items-center gap-space-sm font-code-xs text-code-xs">
            <div className="flex items-center gap-space-xs px-space-sm py-space-2xs bg-surface-container rounded border border-surface-container-high">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span className="text-on-surface-variant">SYS:</span>
              <span className="text-on-surface font-semibold">
                {health?.status === "healthy" ? "OPERATIONAL" : "DEGRADED"}
              </span>
            </div>

            <div className="flex items-center gap-space-xs px-space-sm py-space-2xs bg-surface-container rounded border border-surface-container-high">
              <span className="w-2 h-2 rounded-full bg-primary-container"></span>
              <span className="text-on-surface-variant">MCP:</span>
              <span className="text-primary font-semibold">
                {health?.grafana_mcp_mode === "live" ? "CONNECTED" : "MOCK"}
              </span>
            </div>

            {(() => {
              const isOffline = health?.postwire_ai_mode === "offline";
              const isFallback =
                report?.summary.toLowerCase().includes("fallback") ||
                report?.summary.toLowerCase().includes("quota");

              let statusText = "GOOGLE ADK + GEMINI";
              let dotClass = "bg-tertiary-container animate-ping";
              let textClass = "text-tertiary";

              if (isOffline) {
                statusText = "DETERMINISTIC ENGINE";
                dotClass = "bg-surface-bright";
                textClass = "text-on-surface";
              } else if (isFallback) {
                statusText = "GOOGLE ADK + SAFETY FALLBACK";
                dotClass = "bg-primary-container animate-pulse";
                textClass = "text-primary";
              }

              return (
                <div className="flex items-center gap-space-xs px-space-sm py-space-2xs bg-surface-container rounded border border-surface-container-high">
                  <span className={`w-2 h-2 rounded-full ${dotClass}`}></span>
                  <span className="text-on-surface-variant">AI RUNTIME:</span>
                  <span className={`font-semibold ${textClass}`} title={report?.summary || ""}>
                    {statusText}
                  </span>
                </div>
              );
            })()}

            <div className="flex items-center gap-space-xs px-space-sm py-space-2xs bg-surface-container-lowest rounded border border-outline-variant/30 text-outline">
              <span className="material-symbols-outlined text-[13px]">dns</span>
              <span>prod-us-east-release</span>
            </div>
          </div>

          <div className="h-4 w-px bg-surface-container-highest hidden sm:block"></div>

          <button
            onClick={onReInvestigate}
            disabled={isInvestigating}
            className="p-space-xs text-on-surface-variant hover:text-on-surface transition-colors rounded hover:bg-surface-container-high"
            title="Re-run Autonomous Investigation"
          >
            <span className={`material-symbols-outlined text-[20px] ${isInvestigating ? "animate-spin text-primary" : ""}`}>
              refresh
            </span>
          </button>

          <button className="p-space-xs text-on-surface-variant hover:text-on-surface transition-colors rounded hover:bg-surface-container-high relative">
            <span className="material-symbols-outlined text-[20px]">notifications</span>
            {isCritical && <span className="absolute top-1 right-1 w-2 h-2 bg-error rounded-full"></span>}
          </button>

          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shadow-inner">
            <span className="material-symbols-outlined text-on-primary text-[18px]">person</span>
          </div>
        </div>
      </div>
    </header>
  );
};
