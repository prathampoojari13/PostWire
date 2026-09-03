import React from "react";

interface SidebarProps {
  activeTab: string;
  onNavigate: (tab: string) => void;
  onOpenTerminal: () => void;
  onOpenSettings: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onNavigate,
  onOpenTerminal,
  onOpenSettings,
}) => {
  return (
    <aside className="fixed left-0 top-16 bottom-0 w-14 bg-surface-container-lowest border-r border-surface-container-high z-40 flex flex-col justify-between items-center py-space-md">
      <div className="flex flex-col items-center gap-space-md">
        <button
          onClick={() => onNavigate("overview")}
          className={`p-space-sm rounded transition-colors ${
            activeTab === "overview"
              ? "text-primary bg-surface-container-high"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          }`}
          title="War Room Operations (Overview)"
        >
          <span className="material-symbols-outlined text-[20px]">emergency_home</span>
        </button>

        <button
          onClick={() => onNavigate("incidents")}
          className={`p-space-sm rounded transition-colors ${
            activeTab === "incidents"
              ? "text-primary bg-surface-container-high"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          }`}
          title="Live Incident Stream &amp; Commander Decision"
        >
          <span className="material-symbols-outlined text-[20px]">warning</span>
        </button>

        <button
          onClick={() => onNavigate("releases")}
          className={`p-space-sm rounded transition-colors ${
            activeTab === "releases"
              ? "text-primary bg-surface-container-high"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          }`}
          title="Release Anomaly Differentiation"
        >
          <span className="material-symbols-outlined text-[20px]">rocket_launch</span>
        </button>

        <button
          onClick={() => onNavigate("viewer-qoe")}
          className={`p-space-sm rounded transition-colors ${
            activeTab === "viewer-qoe"
              ? "text-primary bg-surface-container-high"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          }`}
          title="Viewer Telemetry Matrix &amp; Regional QoE"
        >
          <span className="material-symbols-outlined text-[20px]">monitoring</span>
        </button>

        <button
          onClick={() => onNavigate("grafana")}
          className={`p-space-sm rounded transition-colors ${
            activeTab === "grafana"
              ? "text-primary bg-surface-container-high"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          }`}
          title="Grafana Observability &amp; Telemetry"
        >
          <span className="material-symbols-outlined text-[20px]">troubleshoot</span>
        </button>

        <button
          onClick={() => onNavigate("investigation-history")}
          className={`p-space-sm rounded transition-colors ${
            activeTab === "investigation-history"
              ? "text-primary bg-surface-container-high"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          }`}
          title="Audit &amp; Post-Mortem Investigation History"
        >
          <span className="material-symbols-outlined text-[20px]">history_toggle_off</span>
        </button>
      </div>

      <div className="flex flex-col items-center gap-space-sm">
        <button
          onClick={onOpenTerminal}
          className="p-space-sm rounded text-on-surface-variant hover:text-tertiary hover:bg-surface-container-high transition-colors"
          title="Terminal Overlay (Live MCP Stream)"
        >
          <span className="material-symbols-outlined text-[20px]">terminal</span>
        </button>
        <button
          onClick={onOpenSettings}
          className="p-space-sm rounded text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-colors"
          title="Autonomous Agent &amp; MCP Settings"
        >
          <span className="material-symbols-outlined text-[20px]">smart_toy</span>
        </button>
      </div>
    </aside>
  );
};
