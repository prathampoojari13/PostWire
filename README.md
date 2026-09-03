# PostWire — Autonomous Streaming Release Incident Commander

> **Google Cloud Agentic Cinema Hackathon**  
> **Target Partner Track:** Grafana  
> **Core AI:** Google Cloud Agent Builder & Google Gemini  
> **Architecture:** Autonomous Commander Agent + specialized investigation tools

---

## The Core Thesis

During a blockbuster movie premiere, streaming traffic can jump **8x to 10x** in minutes. Traditional threshold-based monitoring systems fire alerts assuming an incident, even when edge CDNs and origins are running smoothly. Conversely, a severe DRM key-server bottleneck on SmartTVs in a single region can be completely masked by healthy global numbers.

> **"PostWire doesn't ask whether traffic is unusual; it asks whether the unusual traffic matters to viewers."**

PostWire combines:
1. **Movie Release Context** (premiere schedules, marketing tiers, expected traffic multipliers, high-value devices)
2. **Viewer Quality-of-Experience (QoE) Telemetry** (join time, rebuffering, fatal playback failures, exit-before-video-start)
3. **Grafana Infrastructure Telemetry via MCP** (edge ingress RPS, CDN cache hit ratio, origin request rate, Loki error logs, DRM latency)

---

## Agentic Architecture

Rather than daisy-chaining multiple slow agents, PostWire uses **one unified Autonomous Commander Agent** equipped with specialized investigation tools:

```
                            +-----------------------------------------------+
                            |        Streaming Anomaly / SRE Alert          |
                            +-----------------------------------------------+
                                                   |
                                                   v
                            +-----------------------------------------------+
                            |           PostWire Commander Agent            |
                            +-----------------------------------------------+
                                                   |
                       +---------------------------+---------------------------+
                       |                           |                           |
                       v                           v                           v
          [ Release Context Tool ]     [ Viewer QoE Analytics ]     [ Grafana MCP Client ]
          - Title & Premiere Window    - Viewer Impact Score (VIS)  - PromQL (RPS, Cache)
          - Expected Surge Multiplier  - Multi-Dimensional Slices   - Loki (Error Logs)
          - High-Value Target Devices  - Regional Dropouts          - Active Alerts
                       |                           |                           |
                       +---------------------------+---------------------------+
                                                   |
                                                   v
                            +-----------------------------------------------+
                            |   Evidence Correlation & Hypothesis Testing   |
                            +-----------------------------------------------+
                                                   |
                                                   v
                            +-----------------------------------------------+
                            |              Incident Decision                |
                            |  - EXPECTED_PREMIERE_SURGE                    |
                            |  - INVESTIGATE                                |
                            |  - CRITICAL_STREAMING_INCIDENT                |
                            |  - Root Cause Hypothesis                      |
                            |  - [SIMULATED] Mitigation Recommendation      |
                            +-----------------------------------------------+
```

### The Autonomous Investigation Loop
1. **ALERT**: Receives ingress or QoE threshold warning.
2. **Context Inspection**: Queries release schedule to determine if surge corresponds to a scheduled cinema premiere.
3. **Hypothesis Formation**: Assesses if traffic spike is expected or indicates infrastructure failure.
4. **Tool Execution**: Dynamically queries Grafana telemetry via MCP and multidimensional viewer QoE data.
5. **Dimensional Slicing**: Evaluates whether global traffic hides localized regional/device failures.
6. **Correlation**: Links infrastructure anomalies (e.g. DRM license timeouts) directly to viewer impact.
7. **Incident Classification**: Emits classification, confidence, concrete evidence, and non-CoT investigation steps.
8. **Mitigation**: Generates a structured operational recommendation explicitly marked `[SIMULATED]`.

---

## Grafana MCP Integration

Grafana MCP is a **core runtime dependency** for the final hackathon submission.

| Mode | Environment | Description |
|---|---|---|
| `mock` | Local Dev & CI Tests | Deterministic mock adapter simulating official Grafana MCP tool responses (`query_prometheus`, `query_loki`, `list_alerts`) mapped to scenario telemetry. **Zero fake claims: labeled as mock.** |
| `live` | Hackathon Demo / Staging | Real client connecting via standard MCP JSON-RPC protocol to the official `@grafana/mcp-grafana` server backed by Grafana Cloud (Prometheus + Loki). |

---

## Demo Scenarios

### Scenario 1: `normal_movie_premiere`
- **Context:** Global day-and-date premiere of *"CyberDune 2: Galactic Reckoning"*.
- **Telemetry:** Global ingress requests surge ~8x (from 180k to 1.44M rps).
- **Infra:** CDN cache hit ratio remains stable at 97.5%.
- **Viewer QoE:** Playback failure rate is <0.05%, join time ~850ms (Viewer Impact Score < 5.0).
- **Commander Decision:** `EXPECTED_PREMIERE_SURGE` (Confidence: 0.98).
- **Action:** No incident opened; alerts suppressed as expected launch demand.

### Scenario 2: `regional_streaming_incident`
- **Context:** Regional premiere of *"Neon Tokyo: Origins"*.
- **Telemetry:** Aggregate global traffic appears normal (1.15x baseline).
- **Anomalous Slice:** SmartTV viewers in `apac-south` experience 14.8% fatal playback failures and join-time spikes.
- **Grafana MCP Telemetry:** PromQL reveals DRM latency >1500ms; Loki logs reveal `PoolExhaustionException` on regional keystore proxy.
- **Commander Decision:** `CRITICAL_STREAMING_INCIDENT` (Confidence: 0.96).
- **Mitigation:** `[SIMULATED] Immediately reroute apac-south SmartTV DRM license requests to secondary healthy key-server cluster in AP-East.`

---

## Project Structure

```
postwire/
├── agent/
│   ├── commander.py          # Autonomous Commander Agent
│   ├── runtime.py            # Modular AI runtime (Agent Builder / Gemini / Offline)
│   ├── prompts.py            # Non-CoT incident investigation system prompts
│   └── tools/
│       ├── grafana_mcp_tools.py # Grafana MCP tools (PromQL, Loki, Alerts)
│       └── qoe_tools.py      # QoE analytics and cinema release context tools
├── telemetry/
│   ├── models.py             # Pydantic models for streaming metrics & reports
│   ├── generator.py          # Multi-dimensional OTT synthetic telemetry generator
│   └── scenarios/
│       ├── premiere_surge.py    # Deterministic Scenario 1 (8x surge)
│       └── regional_incident.py # Deterministic Scenario 2 (APAC DRM failure)
├── grafana/
│   └── integration/
│       ├── interface.py       # Formal MCP client abstract interface
│       ├── mock_mcp_client.py # Local dev mock adapter
│       └── live_mcp_client.py # Official Grafana MCP client (JSON-RPC)
├── qoe/
│   └── viewer_analytics.py   # Viewer Impact Score (VIS) & slice detector
├── api/
│   └── server.py             # FastAPI REST endpoints
├── tests/                    # Deterministic pytest suite (100% passing)
├── config.py                 # Pydantic application settings
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
├── Dockerfile                # Production container spec
└── README.md
```

---

## Quickstart & Local Development

### 1. Prerequisites
- Python 3.11+
- Virtual environment (optional but recommended)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-org/postwire.git
cd PostWire

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit .env:
# - Set GEMINI_API_KEY if testing live Gemini tool-calling
# - Set GRAFANA_MCP_MODE=mock for local offline testing
```

### 4. Run Automated Test Suite
```bash
python -m pytest -v
```
All tests validate telemetry schemas, scenario generation, Grafana MCP adapters, and autonomous Commander decisions.

### 5. Launch PostWire API Server
```bash
python -m uvicorn postwire.api.server:app --reload --port 8000
```
API Documentation is available at `http://localhost:8000/docs`.

---

## API Endpoints

- `GET /health`: Health status and integration modes.
- `GET /api/scenarios`: List demo scenarios.
- `POST /api/scenarios/{scenario_id}/investigate`: Trigger autonomous Commander investigation loop.
- `GET /api/scenarios/{scenario_id}/telemetry`: Inspect multi-dimensional telemetry points.

---

## Milestone 2 Roadmap (TODO for Next Milestone)

- [ ] **Real Grafana Cloud Setup**: Provision Grafana Cloud Prometheus and Loki instances with streaming dashboards.
- [ ] **Official Grafana MCP Connection**: Connect live `@grafana/mcp-grafana` server over MCP transport with service account credentials.
- [ ] **Google Cloud Agent Builder Deployment**: Deploy PostWire Commander using Google Cloud Agent Builder runtime with live Gemini function calling.
- [ ] **Grafana Dashboard JSON**: Export cinema release streaming observability dashboard for the Grafana marketplace.
- [ ] **PostWire Incident Cockpit UI**: Build modern dark-mode frontend showcasing the live investigation timeline, evidence discovery cards, and real-time QoE graphs.
- [ ] **Final 3-Minute Demo Video**: Record end-to-end incident walkthrough showcasing both premiere surge and regional incident resolution.
