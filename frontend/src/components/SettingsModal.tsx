import React from "react";
import type { HealthStatus } from "../api/client";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  health: HealthStatus | null;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  health,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-surface-container-lowest/80 backdrop-blur-md flex items-center justify-center p-space-lg">
      <div className="bg-surface-container w-full max-w-xl rounded-xl p-space-xl shadow-2xl flex flex-col gap-space-lg border border-surface-container-high">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-space-sm">
            <span className="material-symbols-outlined text-secondary text-[22px]">smart_toy</span>
            <span className="font-headline-md text-headline-md text-on-surface">
              Autonomous Agent &amp; MCP Settings
            </span>
          </div>
          <button
            className="p-space-xs text-on-surface-variant hover:text-on-surface rounded"
            onClick={onClose}
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        <div className="flex flex-col gap-space-md font-body-sm text-body-sm text-on-surface">
          <div className="p-space-md bg-surface-container-lowest rounded-lg border border-surface-container-high flex flex-col gap-space-xs">
            <span className="font-label-caps text-label-caps text-tertiary uppercase">AI Engine Architecture</span>
            <div className="flex items-center justify-between mt-1">
              <span className="text-on-surface-variant">Framework:</span>
              <span className="font-semibold text-on-surface">Google Agent Development Kit (ADK)</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-on-surface-variant">Configured Model:</span>
              <span className="font-mono text-primary">{health?.gemini_model || "gemini-3.6-flash"}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-on-surface-variant">Runtime Strategy:</span>
              <span className="font-mono text-secondary">{health?.commander_ai_runtime || "Google ADK Agent"}</span>
            </div>
          </div>

          <div className="p-space-md bg-surface-container-lowest rounded-lg border border-surface-container-high flex flex-col gap-space-xs">
            <span className="font-label-caps text-label-caps text-tertiary uppercase">Grafana Cloud MCP Server</span>
            <div className="flex items-center justify-between mt-1">
              <span className="text-on-surface-variant">Server Binary:</span>
              <span className="font-mono text-on-surface">{health?.grafana_mcp_command || "mcp-grafana"}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-on-surface-variant">Transport:</span>
              <span className="font-semibold text-on-surface">stdio JSON-RPC (MCP v1.3.0)</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-on-surface-variant">Endpoint:</span>
              <span className="font-mono text-tertiary">nimbleelk3407.grafana.net</span>
            </div>
          </div>

          <div className="p-space-sm bg-surface-container-high/40 rounded flex items-start gap-space-xs text-on-surface-variant font-code-xs text-code-xs">
            <span className="material-symbols-outlined text-outline text-[16px] shrink-0 mt-0.5">verified_user</span>
            <span>Safety Policy: Autonomous commands operate strictly in advisory mode. Production routing executes only in simulation sandbox.</span>
          </div>
        </div>

        <div className="flex items-center justify-end">
          <button
            className="px-space-lg py-space-xs bg-primary-container hover:bg-primary-container/90 text-on-primary-container font-headline-sm text-headline-sm font-bold rounded shadow"
            onClick={onClose}
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
