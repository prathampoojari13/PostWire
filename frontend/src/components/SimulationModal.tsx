import React from "react";
import type { SimulationActionResponse } from "../api/client";

interface SimulationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  simulation: SimulationActionResponse | null;
}

export const SimulationModal: React.FC<SimulationModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  simulation,
}) => {
  if (!isOpen || !simulation) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-surface-container-lowest/80 backdrop-blur-md flex items-center justify-center p-space-lg"
      id="simulation-modal"
    >
      <div className="bg-surface-container w-full max-w-2xl rounded-xl p-space-xl shadow-2xl flex flex-col gap-space-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-space-sm">
            <span className="w-3 h-3 rounded-full bg-primary animate-ping"></span>
            <span className="font-headline-md text-headline-md text-on-surface">
              DRM Failover Rebalancing Simulation
            </span>
          </div>
          <button
            className="p-space-xs text-on-surface-variant hover:text-on-surface rounded"
            onClick={onClose}
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        <div className="p-space-md bg-surface-container-lowest rounded-lg font-code-xs text-code-xs text-on-surface flex flex-col gap-space-xs">
          <div className="text-tertiary">[POSTWIRE SIMULATOR v4.19] Evaluating target reroute...</div>
          <div className="text-on-surface-variant">&gt; Target cluster: {simulation.target_cluster}</div>
          <div className="text-on-surface-variant">&gt; Projected latency: {simulation.projected_ttfb}</div>
          <div className="text-primary">&gt; Predicted playback failure reduction: {simulation.projected_playback_failure_reduction}</div>
          <div className="text-emerald-400 font-bold">&gt; SAFETY CHECK: {simulation.safety_check}</div>
          <div className="text-outline italic">&gt; {simulation.message} (Executed: {simulation.executed ? "YES" : "NO"})</div>
        </div>

        <div className="flex items-center justify-end gap-space-md">
          <button
            className="px-space-lg py-space-xs bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-headline-sm text-headline-sm rounded"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            className="px-space-lg py-space-xs bg-primary-container hover:bg-primary-container/90 text-on-primary-container font-headline-sm text-headline-sm font-bold rounded shadow-lg flex items-center gap-space-xs"
            id="btn-apply-sim"
            onClick={onConfirm}
          >
            <span className="material-symbols-outlined text-[16px]">play_arrow</span>
            Authorize Routing Execution
          </button>
        </div>
      </div>
    </div>
  );
};
