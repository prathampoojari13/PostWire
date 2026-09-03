import React from "react";
import type { HealthStatus, IncidentReport } from "../api/client";

interface TerminalDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  health: HealthStatus | null;
  report: IncidentReport | null;
}

export const TerminalDrawer: React.FC<TerminalDrawerProps> = ({
  isOpen,
  onClose,
  health,
  report,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-surface-container-lowest/80 backdrop-blur-md flex items-center justify-center p-space-lg">
      <div className="bg-surface-container w-full max-w-3xl rounded-xl p-space-xl shadow-2xl flex flex-col gap-space-md border border-primary-container/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-space-sm">
            <span className="material-symbols-outlined text-primary text-[20px]">terminal</span>
            <span className="font-headline-md text-headline-md text-on-surface">
              PostWire Commander SRE Terminal &amp; MCP CLI Stream
            </span>
          </div>
          <button
            className="p-space-xs text-on-surface-variant hover:text-on-surface rounded"
            onClick={onClose}
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        <div className="p-space-md bg-surface-container-lowest rounded-lg font-code-xs text-code-xs text-on-surface flex flex-col gap-space-xs max-h-96 overflow-y-auto border border-surface-container-high">
          <div className="text-tertiary font-bold">[POSTWIRE SRE WAR ROOM TERMINAL] — INITIALIZED</div>
          <div className="text-outline">HOST: 127.0.0.1:8000 | ENV: {health?.environment || "development"}</div>
          <div className="text-on-surface-variant">&gt; MCP Runtime: {health?.grafana_mcp_command || "mcp-grafana"}</div>
          <div className="text-on-surface-variant">&gt; MCP Active Mode: {health?.grafana_mcp_active_mode || "live"}</div>
          <div className="text-primary">&gt; Google ADK Model: {health?.gemini_model || "gemini-3.6-flash"}</div>
          <div className="text-secondary">&gt; AI Runtime Status: {health?.commander_ai_runtime || "Active"}</div>
          <div className="text-outline">--------------------------------------------------</div>
          <div className="text-on-surface font-semibold">&gt; Last Correlated Incident: {report?.incident_id || "inc_none"}</div>
          <div className="text-on-surface-variant">&gt; Classification: {report?.classification || "NOMINAL"}</div>
          <div className="text-emerald-400">&gt; Recorded MCP Tools: {report?.investigation_steps?.length || 7} operations executed</div>
          {report?.investigation_steps?.map((s) => (
            <div key={s.step_number} className="text-on-surface-variant pl-space-sm">
              &gt; [Step #{s.step_number}] {s.tool_used} &rarr; {s.query_summary}
            </div>
          ))}
          <div className="text-outline">--------------------------------------------------</div>
          <div className="text-primary-fixed-dim">&gt; Standby for operator command input...</div>
        </div>

        <div className="flex items-center justify-end">
          <button
            className="px-space-lg py-space-xs bg-surface-container-high hover:bg-surface-bright text-on-surface font-headline-sm text-headline-sm rounded"
            onClick={onClose}
          >
            Close Terminal
          </button>
        </div>
      </div>
    </div>
  );
};
