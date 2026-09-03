# PostWire — Autonomous Streaming Release Incident Commander

> **Google Cloud Agentic Cinema Hackathon**  
> **Target Partner Track:** Grafana  
> **Core AI:** Google ADK + Google Gemini  
> **Architecture:** Autonomous Incident Commander Agent + specialized investigation tools  

PostWire is an autonomous streaming incident commander designed for blockbuster movie releases.

It combines **movie-release context, viewer Quality of Experience (QoE), and Grafana infrastructure telemetry** to determine whether an unusual traffic pattern is an expected premiere surge or a real viewer-impacting incident.

> **“PostWire doesn't ask whether traffic is unusual; it asks whether the unusual traffic matters to viewers.”**

---

## 🎯 The Problem

During a major movie premiere, streaming traffic can increase by **8×–10× within minutes**.

A traditional monitoring system may immediately raise an incident because traffic crossed a threshold—even when the CDN, origin, and viewer experience are healthy.

The opposite problem is more dangerous:

A severe infrastructure failure can affect a specific **region + device combination** while global metrics remain mostly healthy.

For example:

* Global traffic: only **1.2×**
* APAC-South SmartTV DRM latency: **~1,850 ms**
* Playback failures: **14.8%**
* HTTP 504 timeouts: **8.4%**
* Viewer impact: severe

A simple global threshold may miss this completely.

PostWire is designed to connect those signals.

---

# 🧠 What PostWire Does

When an alert or anomaly appears, PostWire's Commander Agent investigates dynamically.

```text
                    ALERT / ANOMALY
                           │
                           ▼
              ┌────────────────────────┐
              │  PostWire Commander     │
              │  Google ADK + Gemini    │
              └────────────┬───────────┘
                           │
                    Dynamic Tool Choice
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   Release Context     Viewer QoE      Grafana MCP
   ───────────────     ───────────     ───────────
   Premiere window     Failure rate    Prometheus
   Expected surge      Rebuffering     Loki
   Target devices      VIS             Alerting
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                Evidence Correlation
                           │
                           ▼
                 Incident Classification
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
      Expected Premiere          Critical Incident
           Surge                       │
                                       ▼
                              Root Cause + Evidence
                                       │
                                       ▼
                             [SIMULATED] Mitigation
```

The Commander does **not** blindly analyze every signal.

It chooses investigation tools based on the evidence available and records the investigation as a structured trace.

---

# 🤖 Agentic Architecture

PostWire uses **one autonomous Incident Commander Agent** built with the official Google ADK framework.

Instead of chaining multiple independent LLM agents, the Commander dynamically selects specialized tools.

### Commander Tools

| Tool                       | Purpose                                                           |
| -------------------------- | ----------------------------------------------------------------- |
| `get_release_context`      | Premiere schedule, expected traffic multiplier and target devices |
| `inspect_viewer_qoe`       | Viewer QoE and impact analysis                                    |
| `query_grafana_prometheus` | PromQL infrastructure investigation                               |
| `query_grafana_loki`       | LogQL error investigation                                         |
| `list_grafana_alerts`      | Grafana alert inspection                                          |

The agent can investigate, correlate evidence, classify the incident, and produce a structured decision.

Private chain-of-thought is **not exposed**. The application displays only the investigation trace, selected tools, evidence, decision, confidence, and recommendation.

---

# 🔎 Dynamic Investigation Flow

### 1. Alert

PostWire receives an anomaly such as:

```text
Elevated traffic
Playback failures
Regional QoE degradation
Infrastructure errors
```

### 2. Form an investigation hypothesis

The Commander determines what evidence is needed next.

For a traffic surge:

```text
Traffic anomaly
      ↓
Release context
      ↓
Expected premiere surge?
      ↓
Viewer QoE
      ↓
Expected or incident?
```

For a regional failure:

```text
Regional QoE degradation
      ↓
Region + device analysis
      ↓
Grafana Prometheus
      ↓
Grafana Loki
      ↓
Infrastructure correlation
      ↓
Root-cause hypothesis
```

### 3. Correlate Evidence

PostWire correlates:

* Release expectations
* Traffic
* Viewer failures
* Device-specific QoE
* Regional behavior
* Infrastructure metrics
* Error logs
* Grafana alerts

### 4. Structured Decision

The Commander produces an `IncidentDecision` containing:

* Classification
* Confidence
* Evidence
* Root-cause hypothesis
* Investigation trace
* Recommended mitigation

### 5. Safe Mitigation Recommendation

Operational recommendations are explicitly marked:

```text
[SIMULATED]
```

PostWire **does not modify production traffic, DRM infrastructure, or routing**.

---

# 🎬 Demo Scenarios

PostWire includes two deterministic scenarios for demonstrating the difference between an expected premiere and a real incident.

## Scenario 1 — Normal Premiere

**CyberDune 2**

```text
Expected traffic:        ~8×
CDN cache hit ratio:     ~97.5%
Viewer QoE:              Healthy
Playback failures:      ~0.6%
```

PostWire identifies the traffic spike as:

```text
EXPECTED_PREMIERE_SURGE
```

The key insight:

> High traffic alone does not mean an incident.

---

## Scenario 2 — Regional Streaming Incident

**Neon Tokyo: Origins**

```text
Region:                  APAC-South
Global traffic:         ~1.2×
SmartTV DRM latency:    ~1,850 ms
HTTP 504 timeouts:      ~8.4%
Playback failures:     ~14.8%
EBVS:                    ~9.2%
```

The global traffic level is nowhere near the expected premiere surge.

However, PostWire identifies severe viewer impact localized to:

```text
APAC-South
      +
SmartTV
      +
DRM / Key infrastructure
```

Classification:

```text
CRITICAL_STREAMING_INCIDENT
```

Recommended action:

```text
[SIMULATED]
Reroute APAC-South SmartTV DRM traffic
to a secondary healthy key cluster.
```

The recommendation is advisory only and requires operator authorization.

---

# 🔌 Official Grafana MCP Integration

PostWire integrates with the **official Grafana MCP server (`mcp-grafana`)**.

Communication uses standard:

```text
stdio
  ↓
JSON-RPC
  ↓
Model Context Protocol
```

Architecture:

```text
┌───────────────────────────────────────────┐
│       PostWire Commander Agent            │
│       Google ADK + Gemini                 │
└─────────────────────┬─────────────────────┘
                      │
                      │ MCP / stdio JSON-RPC
                      ▼
┌───────────────────────────────────────────┐
│       Official Grafana MCP Server         │
│              mcp-grafana                  │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│              Grafana Cloud                │
│                                           │
│  Prometheus  │  Loki  │  Alerting        │
└───────────────────────────────────────────┘
```

## Verified Capabilities

The live integration was verified for:

* Official `mcp-grafana`
* MCP handshake
* Tool discovery
* Datasource discovery
* Prometheus connectivity
* Loki connectivity
* Grafana alerting
* PostWire → MCP → Grafana Cloud communication

The integration discovered **81 Grafana MCP tools** during verification.

### Prometheus

PostWire can execute PromQL through Grafana MCP for metrics such as:

* Edge ingress request rate
* CDN cache hit ratio
* Error rates
* Regional infrastructure behavior
* DRM-related latency

### Loki

PostWire can execute LogQL through Grafana MCP for:

* Error signatures
* Timeout patterns
* Regional failures
* Infrastructure logs

### Alerting

Grafana alert rules can also be inspected through the MCP integration.

---

# 🌐 Reality Matrix

PostWire intentionally separates **real infrastructure integrations** from **synthetic demonstration data**.

| Component            | Status        | Details                              |
| -------------------- | ------------- | ------------------------------------ |
| Google Gemini        | **REAL**      | Gemini via official Google SDK / ADK |
| Google ADK           | **REAL**      | Official `google-adk` Agent + Runner |
| Grafana MCP          | **REAL**      | Official `mcp-grafana` integration   |
| Grafana Cloud        | **REAL**      | Live Grafana Cloud integration       |
| Prometheus           | **REAL**      | Live PromQL queries through MCP      |
| Loki                 | **REAL**      | Live LogQL queries through MCP       |
| Grafana Alerting     | **REAL**      | Live alert inspection                |
| Streaming telemetry  | **SIMULATED** | Synthetic OTT time-series            |
| Viewer datasets      | **SIMULATED** | Synthetic Region × Device QoE data   |
| Mitigation execution | **SIMULATED** | No production changes are performed  |

This distinction is intentional and keeps the demonstration technically honest.

---

# 🛡️ Gemini Safety Fallback

PostWire is designed to remain operational if Gemini is temporarily unavailable or quota-limited.

Normal execution:

```text
Google ADK
    ↓
Gemini
    ↓
Commander investigation
```

If Gemini returns a quota or availability failure:

```text
Google ADK
    ↓
Gemini unavailable
    ↓
Deterministic Safety Fallback
    ↓
Structured incident decision
```

The UI explicitly identifies when the safety fallback is active.

This prevents the monitoring system from becoming unavailable simply because the AI reasoning service is temporarily unavailable.

---

# ⚙️ Technology Stack

### AI

* Google Gemini (`gemini-3.6-flash`)
* Google ADK
* `google-genai`
* Autonomous tool selection

### Observability

* Grafana Cloud
* Grafana MCP
* Prometheus
* Loki
* Grafana Alerting

### Backend

* Python
* FastAPI
* Pydantic
* MCP client
* Synthetic telemetry engine
* QoE analytics

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS

---

# 🔐 Configuration

Create a local `.env` file.

**Never commit this file to GitHub.**

Example:

```env
# AI
POSTWIRE_AI_MODE=google_adk
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash

# Grafana
POSTWIRE_GRAFANA_MODE=live
POSTWIRE_RUN_GRAFANA_INTEGRATION=true
GRAFANA_URL=https://your-stack.grafana.net
GRAFANA_SERVICE_ACCOUNT_TOKEN=your_grafana_token_here
GRAFANA_MCP_COMMAND=python -m uv tool run mcp-grafana

# Server
PORT=8000
HOST=0.0.0.0
```

For tests and offline development, Grafana can be configured to use the mock/offline mode.

---

# 🧪 Verification & Testing

The final repository contains an automated test suite covering the core system.

Run:

```bash
python -m pytest -q
```

Current final verification:

```text
33 passed
1 skipped
```

The test suite validates:

* Google ADK agent construction
* Tool registration
* Investigation behavior
* Structured decision generation
* Telemetry generation
* QoE analytics
* Deterministic scenarios
* Grafana MCP adapters
* MCP error handling
* Result parsing

---

## Live Grafana Integration Test

Run:

```bash
POSTWIRE_RUN_GRAFANA_INTEGRATION=true python -m pytest tests/test_grafana_mcp.py -k live -v
```

The live integration verifies the connection between:

```text
PostWire
   ↓
Grafana MCP
   ↓
Grafana Cloud
```

---

## Live Grafana Diagnostics

Run:

```bash
python -m postwire.grafana.integration.verify_live
```

The diagnostics verify:

```text
Official mcp-grafana       PASS
MCP handshake              PASS
Tool discovery             PASS
Datasource discovery      PASS
Prometheus connection      PASS
Loki connection            PASS
Alerting connection        PASS
PostWire → MCP → Cloud     PASS
```

---

# 🚀 Running PostWire Locally

## 1. Start the backend

```bash
python -m uvicorn postwire.api.server:app --port 8000 --host 0.0.0.0 --reload
```

## 2. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

---

# 🖥️ Dashboard

The PostWire dashboard provides:

* Incident overview
* Autonomous investigation stream
* Incident classification
* Confidence score
* Evidence trail
* Scenario switching
* Regional QoE matrix
* Grafana observability panels
* Investigation history
* SRE war-room terminal
* Agent and MCP configuration view
* JSON audit-trail export
* Safe mitigation simulation

The interface is designed around an SRE/incident-response workflow rather than a generic chatbot interface.

---

# 🔌 API Endpoints

### Health

```http
GET /health
```

Returns service health and active AI/Grafana runtime information.

### Grafana MCP Tools

```http
GET /api/mcp/tools
```

Lists tools available through the active Grafana MCP integration.

### Grafana Query

```http
POST /api/mcp/query
```

Queries Prometheus or Loki through Grafana MCP.

### Scenarios

```http
GET /api/scenarios
```

Lists available demonstration scenarios.

### Autonomous Investigation

```http
POST /api/scenarios/{scenario_id}/investigate
```

Starts the Commander investigation for a scenario.

### Regional Breakdown

```http
GET /api/scenarios/{scenario_id}/regional-breakdown
```

Returns regional/device QoE analysis.

### Simulated Action

```http
POST /api/actions/simulate
```

Generates a safe mitigation simulation.

No production action is executed.

---

# 📁 Project Structure

```text
PostWire/
├── postwire/
│   ├── agent/
│   ├── api/
│   ├── grafana/
│   ├── telemetry/
│   ├── qoe/
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.tsx
│   │   └── ...
│   └── package.json
│
├── tests/
├── Dockerfile
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

# 🔒 Safety & Security

PostWire follows a conservative incident-response model.

### No production mutation

Recommended mitigations are explicitly:

```text
[SIMULATED]
```

No production routing, DRM systems, or infrastructure are modified.

### No private chain-of-thought exposure

The UI exposes:

* Tool used
* Query
* Result
* Evidence
* Decision
* Confidence
* Recommendation

It does not expose private model reasoning.

### Secrets

Credentials belong only in `.env`.

The repository's `.gitignore` excludes `.env`.

**Never commit API keys, Grafana tokens, passwords, or service credentials.**

---

# 🏆 Why PostWire?

Most monitoring systems answer:

> **“Is this metric abnormal?”**

PostWire asks:

> **“Is this abnormality actually hurting viewers?”**

That distinction matters during high-volume streaming events.

A massive premiere surge can be completely healthy.

A small global traffic change can hide a severe regional DRM failure.

PostWire connects:

```text
Release Expectations
        +
Viewer Experience
        +
Infrastructure Telemetry
        ↓
Context-Aware Incident Decision
```

This enables an SRE to move from:

```text
Alert
  ↓
Search dashboards
  ↓
Check logs
  ↓
Compare regions
  ↓
Check viewer impact
  ↓
Guess root cause
```

to:

```text
Alert
  ↓
PostWire investigates
  ↓
Evidence correlated
  ↓
Incident classified
  ↓
Root cause hypothesis
  ↓
Safe mitigation recommendation
```

---

# 🔮 Future Extensions

Potential future improvements include:

* Real OTT QoE integrations
* Additional streaming observability signals
* Automated runbook execution with strict approval gates
* Historical incident learning
* More sophisticated anomaly detection
* Multi-region capacity forecasting
* Integration with additional incident-management platforms

---

# 👨‍💻 Project

**PostWire — Autonomous Streaming Release Incident Commander**

Built for the **Google Cloud Agentic Cinema Hackathon**, targeting the **Grafana Partner Track**.

The project demonstrates how an autonomous AI incident commander can combine **Google ADK + Gemini + Grafana MCP + viewer QoE context** to reason about streaming incidents while keeping operational actions safe and explicitly simulated.
