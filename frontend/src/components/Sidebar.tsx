import React from "react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <aside className="fixed left-0 top-16 bottom-0 w-14 bg-surface-container-lowest border-r border-surface-container-high z-40 flex flex-col justify-between items-center py-space-md">
      <div className="flex flex-col items-center gap-space-md">
        <button
          onClick={() => setActiveTab("overview")}
          className={`p-space-sm rounded transition-colors ${
            activeTab === "overview"
              ? "text-primary bg-surface-container-high"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          }`}
          title="War Room Operations"
        >
          <span className="material-symbols-outlined text-[20px]">emergency_home</span>
        </button>

        <button
          onClick={() => setActiveTab("incidents")}
          className={`p-space-sm rounded transition-colors ${
            activeTab === "incidents"
              ? "text-primary bg-surface-container-high"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          }`}
          title="Live Incident Stream"
        >
          <span className="material-symbols-outlined text-[20px]">warning</span>
        </button>

        <button
          onClick={() => setActiveTab("releases")}
          className={`p-space-sm rounded transition-colors ${
            activeTab === "releases"
              ? "text-primary bg-surface-container-high"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          }`}
          title="Release Deployments"
        >
          <span className="material-symbols-outlined text-[20px]">rocket_launch</span>
        </button>

        <button
          onClick={() => setActiveTab("viewer-qoe")}
          className={`p-space-sm rounded transition-colors ${
            activeTab === "viewer-qoe"
              ? "text-primary bg-surface-container-high"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          }`}
          title="Viewer Telemetry Matrix"
        >
          <span className="material-symbols-outlined text-[20px]">monitoring</span>
        </button>

        <button
          onClick={() => setActiveTab("grafana")}
          className={`p-space-sm rounded transition-colors ${
            activeTab === "grafana"
              ? "text-primary bg-surface-container-high"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          }`}
          title="Grafana Observability"
        >
          <span className="material-symbols-outlined text-[20px]">troubleshoot</span>
        </button>

        <button
          onClick={() => setActiveTab("investigation-history")}
          className={`p-space-sm rounded transition-colors ${
            activeTab === "investigation-history"
              ? "text-primary bg-surface-container-high"
              : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
          }`}
          title="Audit &amp; Post-Mortem Logs"
        >
          <span className="material-symbols-outlined text-[20px]">history_toggle_off</span>
        </button>
      </div>

      <div className="flex flex-col items-center gap-space-sm">
        <button
          className="p-space-sm rounded text-on-surface-variant hover:text-tertiary hover:bg-surface-container-high transition-colors"
          title="Terminal Overlay"
        >
          <span className="material-symbols-outlined text-[20px]">terminal</span>
        </button>
        <button
          className="p-space-sm rounded text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-colors"
          title="Autonomous Agent Settings"
        >
          <span className="material-symbols-outlined text-[20px]">smart_toy</span>
        </button>
      </div>
    </aside>
  );
};
