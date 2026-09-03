import React, { useEffect, useState } from "react";
import { api } from "./api/client";
import type {
  HealthStatus,
  InvestigationResponse,
  RegionalQoEBreakdown,
  SimulationActionResponse,
} from "./api/client";

import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";
import { SimulationModal } from "./components/SimulationModal";
import { Toast } from "./components/Toast";
import { HeroIncident } from "./components/HeroIncident";
import { CommanderStream } from "./components/CommanderStream";
import { IncidentDecision } from "./components/IncidentDecision";
import { AnomalyComparison } from "./components/AnomalyComparison";
import { GrafanaObservability } from "./components/GrafanaObservability";
import { RegionalQoE } from "./components/RegionalQoE";
import { IncidentHistory } from "./components/IncidentHistory";

import { TerminalDrawer } from "./components/TerminalDrawer";
import { SettingsModal } from "./components/SettingsModal";

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [currentScenario, setCurrentScenario] = useState<string>("regional_streaming_incident");
  const [investigation, setInvestigation] = useState<InvestigationResponse | null>(null);
  const [regionalBreakdown, setRegionalBreakdown] = useState<RegionalQoEBreakdown[]>([]);
  const [isInvestigating, setIsInvestigating] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<string>("overview");

  // Interactive Overlays
  const [isTerminalOpen, setIsTerminalOpen] = useState<boolean>(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);

  // Simulation & Toast State
  const [simulationModalOpen, setSimulationModalOpen] = useState<boolean>(false);
  const [simulationData, setSimulationData] = useState<SimulationActionResponse | null>(null);
  const [toast, setToast] = useState<{ show: boolean; title: string; subtitle: string }>({
    show: false,
    title: "",
    subtitle: "",
  });

  // Initial fetch
  useEffect(() => {
    loadHealth();
    runInvestigation("regional_streaming_incident");
  }, []);

  const loadHealth = async () => {
    try {
      const h = await api.getHealth();
      setHealth(h);
    } catch (e) {
      console.warn("Could not load backend health:", e);
    }
  };

  const runInvestigation = async (scenarioId: string) => {
    setIsInvestigating(true);
    setCurrentScenario(scenarioId);
    try {
      const [invRes, regRes] = await Promise.all([
        api.investigateScenario(scenarioId),
        api.getRegionalBreakdown(scenarioId).catch(() => []),
      ]);
      setInvestigation(invRes);
      setRegionalBreakdown(regRes);
      await loadHealth();
    } catch (e) {
      console.error("Investigation error:", e);
    } finally {
      setIsInvestigating(false);
    }
  };

  const handleNavigate = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === "overview") {
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    const targetMap: Record<string, string> = {
      incidents: "section-incidents",
      releases: "section-releases",
      "viewer-qoe": "section-viewer-qoe",
      grafana: "section-grafana",
      "investigation-history": "section-investigation-history",
    };
    const elemId = targetMap[tabId] || `section-${tabId}`;
    const elem = document.getElementById(elemId);
    if (elem) {
      const navOffset = 80;
      const elementPosition = elem.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - navOffset;
      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth",
      });
    }
  };

  const handleOpenSimulation = async () => {
    try {
      const sim = await api.simulateAction(currentScenario, "drm_failover");
      setSimulationData(sim);
      setSimulationModalOpen(true);
    } catch (e) {
      console.error("Simulation request error:", e);
    }
  };

  const handleConfirmSimulation = () => {
    setSimulationModalOpen(false);
    showToast(
      "Simulated Remediation Executed",
      simulationData?.action || "Reroute command queued for operator cluster ap-southeast-1-hsm-b [SIMULATED ONLY]"
    );
  };

  const handleEscalateP0 = () => {
    showToast(
      "Status Broadcast Sent to #sre-war-room",
      `Incident ${investigation?.release_context?.release_id || "rel_neontokyo_2026"} briefed to on-call leadership.`
    );
  };

  const handleExportAuditTrail = () => {
    const dataStr = JSON.stringify(investigation || {}, null, 2);
    const blob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `audit_trail_${investigation?.scenario_id || "incident"}.json`;
    a.click();
    showToast("Audit Trail Exported", "Downloaded JSON audit logs for post-mortem analysis.");
  };

  const showToast = (title: string, subtitle: string) => {
    setToast({ show: true, title, subtitle });
    setTimeout(() => {
      setToast((prev) => ({ ...prev, show: false }));
    }, 4500);
  };

  const report = investigation?.report || null;
  const releaseContext = investigation?.release_context || null;
  const qoe = investigation?.aggregate_qoe || null;

  return (
    <div className="bg-background font-body-sm text-body-sm text-on-surface antialiased min-h-screen">
      {/* Fixed Header */}
      <Header
        health={health}
        releaseContext={releaseContext}
        report={report}
        activeTab={activeTab}
        onNavigate={handleNavigate}
        currentScenario={currentScenario}
        onSwitchScenario={runInvestigation}
        isInvestigating={isInvestigating}
        onReInvestigate={() => runInvestigation(currentScenario)}
      />

      {/* Fixed Left Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onNavigate={handleNavigate}
        onOpenTerminal={() => setIsTerminalOpen(true)}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* Main Content Area matching Stitch DOM */}
      <div className="pl-14">
        <main className="relative pt-16 bg-surface-container-lowest min-h-screen">
          <div className="flex flex-col w-full">
            {/* Interactive Modal Container for Action Simulation */}
            <SimulationModal
              isOpen={simulationModalOpen}
              onClose={() => setSimulationModalOpen(false)}
              onConfirm={handleConfirmSimulation}
              simulation={simulationData}
            />

            {/* SRE War Room Terminal Overlay */}
            <TerminalDrawer
              isOpen={isTerminalOpen}
              onClose={() => setIsTerminalOpen(false)}
              health={health}
              report={report}
            />

            {/* Autonomous Agent Settings Modal */}
            <SettingsModal
              isOpen={isSettingsOpen}
              onClose={() => setIsSettingsOpen(false)}
              health={health}
            />

            {/* Notification Toast */}
            <Toast show={toast.show} title={toast.title} subtitle={toast.subtitle} />

            {/* Content Container */}
            <div className="p-space-lg xl:p-space-2xl flex flex-col gap-space-xl max-w-[1880px] mx-auto w-full">
              {/* 1. TOP BANNER / CRITICAL INCIDENT ALERT HERO */}
              <HeroIncident
                report={report}
                releaseContext={releaseContext}
                qoe={qoe}
                onEscalate={handleEscalateP0}
              />

              {/* 2. CORE COMMAND ROW: INVESTIGATION VS DECISION/MITIGATION */}
              <div id="section-incidents" className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
                <CommanderStream report={report} health={health} />
                <IncidentDecision
                  report={report}
                  onOpenSimulation={handleOpenSimulation}
                  onStatusPost={handleEscalateP0}
                />
              </div>

              {/* 3. PREMIERE ANOMALY COMPARISON */}
              <div id="section-releases">
                <AnomalyComparison
                  report={report}
                  releaseContext={releaseContext}
                  qoe={qoe}
                />
              </div>

              {/* 4. REAL-TIME GRAFANA OBSERVABILITY SECTION */}
              <div id="section-grafana">
                <GrafanaObservability
                  qoe={qoe}
                  health={health}
                  onRefresh={() => runInvestigation(currentScenario)}
                />
              </div>

              {/* 5. VIEWER QUALITY OF EXPERIENCE (QoE) & REGIONAL IMPACT TABLE */}
              <div id="section-viewer-qoe">
                <RegionalQoE
                  qoe={qoe}
                  regionalBreakdown={regionalBreakdown}
                  report={report}
                />
              </div>

              {/* 6. INCIDENT INVESTIGATION HISTORY TABLE */}
              <div id="section-investigation-history">
                <IncidentHistory
                  report={report}
                  releaseContext={releaseContext}
                  onSimulateReroute={handleOpenSimulation}
                  onExportAuditTrail={handleExportAuditTrail}
                />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
