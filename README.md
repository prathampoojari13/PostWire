# PostWire — Autonomous Streaming Release Incident Commander

> **Google Cloud Agentic Cinema Hackathon**  
> **Target Partner Track:** Grafana  
> **Core AI:** Google ADK & Google Gemini  
> **Architecture:** Autonomous Commander Agent + specialized investigation tools

---

## The Core Thesis

During a blockbuster movie premiere, streaming traffic can jump **8x to 10x** in minutes. Traditional threshold-based monitoring systems fire alerts assuming an incident, even when edge CDNs and origins are running smoothly. Conversely, a severe DRM key-server bottleneck on SmartTVs in a single region can be completely masked by healthy global numbers.

> **"PostWire doesn't ask whether traffic is unusual; it asks whether the unusual traffic matters to viewers."**

PostWire correlates:
1. **Movie Release Context** (premiere schedules, marketing tiers, expected surge factors, high-value devices)
2. **Viewer Quality-of-Experience (QoE) Telemetry** (join time, rebuffering, fatal playback failures, exit-before-video-start)
3. **Grafana Infrastructure Telemetry via MCP** (PromQL metrics: edge ingress RPS, CDN cache hit ratio, origin rate; LogQL: Loki error logs; Alerting rules)

---

## Reality Matrix: What is Real vs. Simulated

To adhere to hackathon rules and maintain engineering honesty:

| Component | Status | Implementation Details |
|---|---|---|
| **Google Gemini AI** | **REAL** | Powered by Google Gemini (`gemini-2.5-flash`) via the official `google-genai` SDK and Google Cloud authentication. |
| **Google ADK Agent** | **REAL** | Built with the official `google-adk` framework (`Agent`, `Runner`, `InMemorySessionService`) with dynamic tool execution. |
| **Official Grafana MCP** | **REAL** | Official Go-based `mcp-grafana` server running over standard `stdio` JSON-RPC transport (81 tools discovered). |
| **Grafana Cloud** | **REAL** | Connects to real Grafana Cloud stack (`https://<org>.grafana.net`) with Service Account authentication. |
| **Prometheus Telemetry** | **REAL** | Real PromQL queries executed via `query_prometheus` MCP tool to Grafana Cloud Prometheus. |
| **Loki Log Analytics** | **REAL** | Real LogQL log queries executed via `query_loki_logs` MCP tool to Grafana Cloud Loki. |
| **Grafana Alerting** | **REAL** | Real alert rule inspection executed via `alerting_manage_rules` MCP tool. |
| **Streaming Telemetry** | **SIMULATED** | High-fidelity multi-dimensional synthetic OTT time-series representing cinema premiere spikes and regional bottlenecks. |
| **Viewer Datasets** | **SIMULATED** | Simulated multi-dimensional slices (Region × Device Type) with mathematical distribution of QoE metrics. |
| **Mitigation Execution** | **SIMULATED** | Recommended operational actions are strictly marked `[SIMULATED]`. No production traffic routing or DRM servers are modified. |

---

## Agentic Architecture

Rather than slow sequential multi-agent chaining, PostWire uses **one autonomous Incident Commander Agent** built on Google ADK, dynamically deciding which specialized tool to invoke:

```
                            +-----------------------------------------------+
                            |        Streaming Anomaly / SRE Alert          |
                            +-----------------------------------------------+
                                                   |
                                                   v
                            +-----------------------------------------------+
                            |     PostWire Commander Agent (Google ADK)     |
                            |       Model: Gemini (Configurable via ENV)    |
                            +-----------------------------------------------+
                                                   | (Dynamic Tool Selection)
                        +--------------------------+--------------------------+
                        |                          |                          |
                        v                          v                          v
           [ Release Context Tool ]    [ Viewer QoE Analytics ]    [ Grafana Cloud MCP ]
           - Title & Premiere Window   - Viewer Impact Score (VIS) - PromQL (RPS, Cache)
           - Expected Surge Multiplier - Multi-Dimensional Slices  - LogQL (Loki Error Logs)
           - High-Value Target Devices - Regional Dropouts         - Alerting Rules
                        |                          |                          |
                        +--------------------------+--------------------------+
                                                   |
                                                   v
                            +-----------------------------------------------+
                            |   Evidence Correlation & Hypothesis Testing   |
                            +-----------------------------------------------+
                                                   |
                                                   v
                            +-----------------------------------------------+
                            |         Structured Incident Decision          |
                            |  - EXPECTED_PREMIERE_SURGE                    |
                            |  - INVESTIGATE                                |
                            |  - CRITICAL_STREAMING_INCIDENT                |
                            |  - Root Cause Hypothesis                      |
                            |  - [SIMULATED] Mitigation Recommendation      |
                            +-----------------------------------------------+
```

### Dynamic Investigation Flow
1. **ALERT**: Alert received regarding elevated ingress requests or error threshold warnings.
2. **Dynamic Tool Choice**: The Commander decides what tool to invoke next based on evidence:
   - For traffic surges: inspects movie release context first to see if an 8x surge is scheduled, then inspects viewer QoE.
   - For regional dropouts: inspects viewer QoE slices across regions and devices, then queries Grafana Prometheus and Loki for localized key-server timeouts.
3. **Evidence Correlation**: Correlates infrastructure anomalies with real viewer QoE impact.
4. **Structured Decision**: Outputs a structured `IncidentDecision` (Pydantic) with confidence, evidence list, and investigation trace (no private chain-of-thought).
5. **Simulated Mitigation**: Emits operational recommendations explicitly prefixed with `[SIMULATED]`.

---

## Official Grafana MCP Integration

PostWire connects to the **official Grafana MCP server (`mcp-grafana`)** over the standard Model Context Protocol (MCP) using **standard I/O (`stdio`) JSON-RPC transport**.

```
+-------------------------------------------------------------------------+
|                  PostWire Commander (Google ADK + Gemini)               |
+-------------------------------------------------------------------------+
                                    │ (mcp.client.stdio.stdio_client)
                                    ▼ [stdio JSON-RPC]
+-------------------------------------------------------------------------+
|              Official Grafana MCP Server (mcp-grafana v1.3.0)           |
+-------------------------------------------------------------------------+
                                    │ (Grafana HTTP API / Datasource Proxy)
                                    ▼
+-------------------------------------------------------------------------+
|                              Grafana Cloud                              |
|   ├── Prometheus: Edge Ingress RPS, Cache Hit Ratio, 5xx Rates          |
|   ├── Loki: Application & Edge Proxy Access Logs, Error Signatures      |
|   └── Alerting: Core Alert Rules & Notification Policies                |
+-------------------------------------------------------------------------+
```

### Verified Grafana MCP Capabilities
- **Stdio Protocol Handshake**: Initialized with `mcp-grafana v1.3.0`.
- **Tool Discovery**: Discovers **81 official tools** directly from Grafana Cloud.
- **Dynamic Datasource Discovery**: Automatically discovers `datasourceUid` for Prometheus and Loki using the `list_datasources` tool.
- **Safe Queries**: Executes PromQL via `query_prometheus`, LogQL via `query_loki_logs`, and alert checks via `alerting_manage_rules`.

---

## Configuration & Environment Variables

Configure your local `.env` file (never commit secrets):

```env
# AI Engine Selection: "google_adk" or "offline"
POSTWIRE_AI_MODE=google_adk

# Google Gemini / Google Cloud
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Grafana MCP Integration Mode: "mock" (offline/tests) or "live" (real Grafana Cloud)
POSTWIRE_GRAFANA_MODE=live
POSTWIRE_RUN_GRAFANA_INTEGRATION=true

# Real Grafana Cloud instance credentials
GRAFANA_URL=https://<your-stack-name>.grafana.net
GRAFANA_SERVICE_ACCOUNT_TOKEN=glsa_<your_service_account_token>
GRAFANA_MCP_COMMAND=python -m uv tool run mcp-grafana

# Server Config
PORT=8000
HOST=0.0.0.0
```

---

## Verification & Testing

### 1. Run Complete Automated Test Suite (28 Tests)
```bash
python -m pytest -v
```
Validates:
- Google ADK Agent construction and tool registration
- Dynamic tool capability and non-CoT investigation tracking
- Telemetry generator and QoE analytics (Viewer Impact Score)
- Deterministic scenarios (`normal_movie_premiere` & `regional_streaming_incident`)
- Grafana MCP client adapters, error handlers, and result parsers

### 2. Run Live Grafana Cloud MCP Integration Test
```bash
POSTWIRE_RUN_GRAFANA_INTEGRATION=true python -m pytest tests/test_grafana_mcp.py -k live -v
```

### 3. Run Live Diagnostics Script
```bash
python -m postwire.grafana.integration.verify_live
```
Produces the verified audit scorecard against your real Grafana Cloud stack:
```text
| Check                          | Result    |
|--------------------------------|-----------|
| Official mcp-grafana           | PASS      |
| MCP handshake                  | PASS      |
| tools/list                     | PASS      |
| Datasource discovery           | PASS      |
| Prometheus connection          | PASS      |
| Loki connection                | PASS      |
| Alerting connection            | PASS      |
| PostWire -> MCP -> Cloud       | PASS      |
```

---

## API Endpoints

- `GET /health`: Service health, active AI runtime (`Google ADK Agent` or `Offline`), and Grafana MCP modes.
- `GET /api/mcp/tools`: Lists tools discovered from the active Grafana MCP server.
- `POST /api/mcp/query`: Query Prometheus or Loki through Grafana MCP.
- `GET /api/scenarios`: Lists available streaming demo scenarios.
- `POST /api/scenarios/{scenario_id}/investigate`: Triggers the autonomous Commander investigation loop.
- `GET /api/scenarios/{scenario_id}/telemetry`: Inspects multi-dimensional telemetry time-series.
