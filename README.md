# 🛡️ PostWire — Autonomous Streaming Release Incident Commander

> **AI-powered incident intelligence for streaming platforms — combining movie release context, viewer QoE, and real-time Grafana telemetry to detect, investigate, and respond to release incidents.**

**Version:** `0.2.0`
**Status:** 🟢 Live

### 🚀 Live Demo

**Frontend:**
https://postwire-frontend.onrender.com/

**Backend API:**
https://postwire-kzex.onrender.com/

**API Documentation (Swagger):**
https://postwire-kzex.onrender.com/docs

**OpenAPI Specification:**
https://postwire-kzex.onrender.com/openapi.json

---

## 🎯 What is PostWire?

PostWire is an **autonomous AI incident commander** designed for streaming platforms during high-impact movie and content releases.

When a major release happens, streaming platforms can experience sudden changes in:

* Viewer traffic
* Buffering and playback quality
* Regional availability
* Error rates
* Device-specific performance
* Infrastructure health

PostWire correlates **release context + viewer Quality of Experience (QoE) + infrastructure telemetry** to automatically investigate incidents and recommend corrective actions.

Instead of forcing an SRE to manually inspect multiple dashboards, PostWire acts as an intelligent incident commander.

---

## 🧠 Core Idea

```text
                ┌──────────────────────┐
                │   Movie Release      │
                │      Context         │
                └──────────┬───────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────┐
│                    POSTWIRE                     │
│                                                 │
│        Autonomous AI Incident Commander         │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ Release     │  │ Viewer QoE  │  │ Grafana │ │
│  │ Context     │  │ Telemetry   │  │  MCP    │ │
│  └──────┬──────┘  └──────┬──────┘  └────┬────┘ │
│         │                │              │      │
│         └────────────────┼──────────────┘      │
│                          ▼                     │
│                 ┌────────────────┐             │
│                 │ Gemini + ADK   │             │
│                 │ AI Commander   │             │
│                 └───────┬────────┘             │
│                         ▼                      │
│              Incident Investigation            │
│                         │                      │
│                         ▼                      │
│              Recommended Actions               │
└─────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 🤖 Autonomous Incident Investigation

PostWire uses Gemini-powered reasoning to investigate streaming incidents instead of relying only on static rules.

The AI can:

1. Analyze the release scenario
2. Query available telemetry
3. Correlate QoE signals
4. Identify abnormal patterns
5. Classify the incident
6. Determine likely root causes
7. Recommend remediation actions

---

### 📊 Viewer QoE Analysis

PostWire analyzes viewer experience across multiple dimensions:

* Buffering
* Playback failures
* Startup latency
* Error rates
* Regional performance
* Device performance

This helps distinguish between an infrastructure problem and a localized viewer-experience problem.

---

### 🌍 Regional Breakdown

PostWire provides regional QoE analysis to identify geographic hotspots.

Example:

```text
Region        QoE Status
────────────────────────────
North India   🟢 Healthy
South India   🔴 Degraded
West India    🟡 Warning
East India    🟢 Healthy
```

This allows incident responders to determine whether an issue is:

* Global
* Regional
* Device-specific
* Infrastructure-specific

---

### 📡 Grafana MCP Integration

PostWire connects to Grafana telemetry through MCP.

This allows the incident commander to access operational telemetry and use it as part of its investigation.

The architecture enables AI reasoning over real operational signals rather than relying entirely on predefined datasets.

---

### 🧠 Gemini + Google ADK

The AI incident commander is powered by:

* Google Gemini
* Google ADK
* MCP-based tool execution

The agent can dynamically determine which tools and telemetry sources are relevant to an investigation.

---

### 🧪 Action Simulation

PostWire can simulate recommended remediation actions before they are applied.

Example actions can include:

```text
Traffic rerouting
Regional mitigation
Capacity scaling
Configuration changes
Feature rollback
```

This provides a safer way to evaluate possible responses.

---

## 🔌 API Endpoints

### Health Check

```http
GET /health
```

Checks whether the backend is operational.

### List MCP Tools

```http
GET /api/mcp/tools
```

Returns available MCP tools.

### Query MCP

```http
POST /api/mcp/query
```

Executes an MCP query.

### List Scenarios

```http
GET /api/scenarios
```

Returns available streaming incident scenarios.

### Investigate Scenario

```http
POST /api/scenarios/{scenario_id}/investigate
```

Starts an autonomous investigation for a scenario.

### Regional Breakdown

```http
GET /api/scenarios/{scenario_id}/regional-breakdown
```

Returns regional QoE information.

### Scenario Telemetry

```http
GET /api/scenarios/{scenario_id}/telemetry
```

Returns telemetry associated with a scenario.

### Simulate Action

```http
POST /api/actions/simulate
```

Simulates a proposed remediation action.

---

## 🏗️ Technology Stack

### Frontend

* React 18
* TypeScript
* Vite
* Tailwind CSS

### Backend

* Python
* FastAPI
* Pydantic
* Uvicorn

### AI

* Google Gemini
* Google ADK

### Observability

* Grafana Cloud
* Grafana MCP

### Deployment

* Render

---

## 📁 Project Structure

```text
PostWire/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.*
│   └── ...
│
├── postwire/
│   ├── api/
│   ├── agent/
│   ├── telemetry/
│   ├── scenarios/
│   └── ...
│
├── tests/
│
├── Dockerfile
├── requirements.txt
├── .env.example
├── LICENSE
└── README.md
```

---

## 🔄 How PostWire Works

```text
1. Streaming release begins
            ↓
2. Viewer & infrastructure telemetry changes
            ↓
3. PostWire collects relevant signals
            ↓
4. Grafana MCP provides telemetry
            ↓
5. Gemini AI analyzes the evidence
            ↓
6. Incident is classified
            ↓
7. Regional / device patterns are identified
            ↓
8. Root cause is investigated
            ↓
9. Remediation is recommended
            ↓
10. Action can be simulated
```

---

## 🧩 Incident Intelligence Pipeline

### Step 1 — Detect

Identify unusual changes in streaming performance.

### Step 2 — Correlate

Combine:

* Movie release information
* Viewer QoE
* Regional information
* Infrastructure telemetry

### Step 3 — Investigate

The AI commander queries relevant telemetry and evaluates evidence.

### Step 4 — Classify

The incident is categorized based on observed signals.

### Step 5 — Explain

PostWire produces an investigation report with supporting evidence.

### Step 6 — Recommend

The system suggests potential remediation actions.

### Step 7 — Simulate

Recommended actions can be simulated before being applied.

---

## 🚨 Example Incident

Imagine a major movie launches at 8 PM.

Within minutes:

```text
Traffic             ↑ 320%
Buffering           ↑ 180%
Playback Errors     ↑ 140%
South Region QoE    ↓ 35%
```

Instead of an SRE manually checking multiple dashboards, PostWire correlates the signals.

The AI might determine:

```text
Incident:
Regional streaming degradation

Affected Region:
South India

Likely Cause:
Regional infrastructure capacity pressure

Confidence:
High

Recommended Action:
Scale capacity / reroute traffic
```

The action can then be simulated before operational execution.

---

## 🔐 Environment Variables

For local development, create a `.env` file based on `.env.example`.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.6-flash

GRAFANA_URL=your_grafana_url
GRAFANA_SERVICE_ACCOUNT_TOKEN=your_grafana_token
```

**Never commit real API keys or service-account tokens to GitHub.**

---

## 💻 Local Development

### Backend

Clone the repository:

```bash
git clone https://github.com/prathampoojari13/PostWire.git
cd PostWire
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn postwire.api.server:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

### Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start development server:

```bash
npm run dev
```

The frontend will be available at the local Vite URL shown in the terminal.

---

## ☁️ Production Deployment

PostWire is deployed using **Render**.

### Frontend

```text
Platform: Render Static Site
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
```

### Backend

```text
Platform: Render Web Service
Environment: Docker
```

---

## 🌐 Production URLs

### Frontend

https://postwire-frontend.onrender.com/

### Backend

https://postwire-kzex.onrender.com/

### Swagger API Documentation

https://postwire-kzex.onrender.com/docs

### OpenAPI

https://postwire-kzex.onrender.com/openapi.json

---

## 🧪 API Health

The deployed backend exposes:

```http
GET /health
```

Use it to verify backend availability.

---

## 🏆 Why PostWire?

Traditional incident response often requires engineers to:

```text
Open dashboards
      ↓
Check metrics
      ↓
Compare regions
      ↓
Inspect logs
      ↓
Identify anomalies
      ↓
Find root cause
      ↓
Decide remediation
```

PostWire aims to compress this workflow into:

```text
Telemetry
    ↓
AI Investigation
    ↓
Root Cause
    ↓
Recommended Action
```

The goal is to move incident response from **manual dashboard hunting** toward **autonomous, evidence-driven incident intelligence**.

---

## 🔮 Future Scope

Potential future improvements include:

* Automated remediation execution
* Real-time streaming telemetry
* Multi-agent incident investigation
* Historical incident learning
* Predictive incident detection
* Automated rollback
* Slack / Teams incident notifications
* Advanced anomaly detection
* Continuous SRE feedback loops

---

## 👨‍💻 Author

**Pratham K**

B.E. Computer Science & Engineering
BMS Institute of Technology & Management

---

## 📄 License

This project is licensed under the MIT License.

---

## ⭐ Support

If you find PostWire interesting, consider giving the repository a ⭐ on GitHub.

**GitHub:**
https://github.com/prathampoojari13/PostWire

---

### 🚀 PostWire

> **Observe. Investigate. Reason. Respond.**
