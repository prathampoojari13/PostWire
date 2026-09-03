/**
 * PostWire Incident Commander API Client.
 * Connects to the FastAPI backend on http://localhost:8000 (configurable via VITE_API_BASE_URL).
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  gemini_model: string;
  postwire_ai_mode: string;
  commander_ai_runtime: string;
  postwire_grafana_mode: string;
  grafana_mcp_mode: string;
  grafana_mcp_command: string;
  grafana_mcp_active_mode: string;
  environment: string;
}

export interface ScenarioSummary {
  id: string;
  name: string;
  description: string;
  release_title: string;
  expected_classification: string;
}

export interface MovieReleaseContext {
  release_id: string;
  title: string;
  premiere_window_start: string;
  marketing_tier: string;
  expected_viewer_surge_factor: number;
  high_value_devices: string[];
  description: string;
}

export interface AggregateTelemetry {
  timestamp: string;
  total_concurrent_viewers: number;
  total_request_rate_rps: number;
  avg_cdn_cache_hit_ratio: number;
  total_origin_request_rate_rps: number;
  avg_http_5xx_rate: number;
  avg_manifest_latency_ms: number;
  avg_drm_license_latency_ms: number;
  avg_video_start_time_ms: number;
  avg_rebuffer_ratio: number;
  avg_exit_before_video_start: number;
  avg_playback_failure_rate: number;
  viewer_impact_score: number;
}

export interface InvestigationStep {
  step_number: number;
  tool_used: string;
  query_summary: string;
  evidence_discovered: string;
}

export interface IncidentReport {
  incident_id: string;
  release_id: string;
  timestamp: string;
  classification: "NORMAL" | "EXPECTED_PREMIERE_SURGE" | "CRITICAL_STREAMING_INCIDENT" | "INVESTIGATE";
  confidence: number;
  summary: string;
  evidence: string[];
  recommended_mitigation: string;
  affected_region?: string | null;
  affected_device?: string | null;
  viewer_impact_score?: number | null;
  investigation_steps: InvestigationStep[];
}

export interface RegionalQoEBreakdown {
  region: string;
  concurrent_viewers: number;
  viewer_impact_score: number;
  playback_failure_rate: number;
  rebuffer_ratio: number;
  drm_license_latency_ms: number;
  manifest_latency_ms: number;
  status: "HEALTHY" | "WARNING" | "CRITICAL";
}

export interface InvestigationResponse {
  scenario_id: string;
  alert_event: string;
  release_context: MovieReleaseContext;
  aggregate_qoe: AggregateTelemetry;
  report: IncidentReport;
  regional_breakdown: RegionalQoEBreakdown[];
}

export interface SimulationActionResponse {
  status: string;
  action: string;
  executed: boolean;
  message: string;
  target_cluster: string;
  projected_playback_failure_reduction: string;
  projected_ttfb: string;
  safety_check: string;
}

export const api = {
  /** Check service health and active agent/MCP runtime modes */
  async getHealth(): Promise<HealthStatus> {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error(`Failed to fetch health: ${res.statusText}`);
    return res.json();
  },

  /** List available scenarios */
  async getScenarios(): Promise<ScenarioSummary[]> {
    const res = await fetch(`${API_BASE_URL}/api/scenarios`);
    if (!res.ok) throw new Error(`Failed to fetch scenarios: ${res.statusText}`);
    return res.json();
  },

  /** Trigger autonomous incident investigation for scenario */
  async investigateScenario(scenarioId: string): Promise<InvestigationResponse> {
    const res = await fetch(`${API_BASE_URL}/api/scenarios/${scenarioId}/investigate`, {
      method: "POST",
    });
    if (!res.ok) throw new Error(`Investigation failed: ${res.statusText}`);
    return res.json();
  },

  /** Get regional QoE breakdown for scenario */
  async getRegionalBreakdown(scenarioId: string): Promise<RegionalQoEBreakdown[]> {
    const res = await fetch(`${API_BASE_URL}/api/scenarios/${scenarioId}/regional-breakdown`);
    if (!res.ok) throw new Error(`Failed to fetch regional breakdown: ${res.statusText}`);
    return res.json();
  },

  /** Query Grafana Prometheus or Loki via MCP */
  async queryMCP(queryType: "prometheus" | "loki", query: string, timeRangeOrLimit = "5m"): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/api/mcp/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query_type: queryType,
        query,
        time_range_or_limit: timeRangeOrLimit,
      }),
    });
    if (!res.ok) throw new Error(`MCP query failed: ${res.statusText}`);
    return res.json();
  },

  /** Trigger simulated action mitigation (strictly safe, no production change) */
  async simulateAction(scenarioId: string, actionType = "drm_failover"): Promise<SimulationActionResponse> {
    const res = await fetch(`${API_BASE_URL}/api/actions/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_id: scenarioId, action_type: actionType }),
    });
    if (!res.ok) throw new Error(`Simulation request failed: ${res.statusText}`);
    return res.json();
  },
};
