# SherLock — Autonomous SRE Platform

**Part 1: Data & Intelligence Backend** + **Part 2: API & Dashboard**

AI-powered investigation engine that ingests telemetry, maintains a Neo4j knowledge graph, produces structured `InvestigationResult` JSON, and exposes it via REST API and Next.js dashboard.

---

## Architecture

### Part 1 (Agent, Graph, Evals)

- **Ingestion:** Airbyte + OpenTelemetry Collector → Kafka
- **Graph:** Neo4j (Service, Deployment, Incident, Host nodes)
- **Agent:** LangGraph + GPT-4o → hypotheses, evidence, RCA, recommendations
- **Output:** InvestigationResult JSON → SQS + S3 (Part 2 interface)

### Part 2 (API, Dashboard)

- **API:** FastAPI REST API — investigations, webhooks, remediation, metrics
- **Dashboard:** Next.js 14 — incident feed, service map, KPI dashboard

---

## Quick Start

### Part 1: Agent (investigation engine)

```bash
make install
docker-compose up -d
python -m graph.schema.apply
python -m graph.fixtures.load
make agent
# POST /investigate with {"service_name": "service-1", "description": "Error rate spike"}
```

### Part 2: API + Dashboard

```bash
# API
cd api && pip install -e . && uvicorn src.app.main:app --reload --port 8000

# Dashboard
cd dashboard && npm install && npm run dev
```

- **Agent:** http://localhost:8001  
- **API:** http://localhost:8000  
- **Dashboard:** http://localhost:3000  

---

## Environment

Copy `.env.example` to `.env` and set `NEO4J_URI`, `NEO4J_PASSWORD`, `OPENAI_API_KEY`, `TAVILY_API_KEY`.

---

## Project Structure

```
SherLock/
├── agent/               # Part 1: LangGraph investigation engine
├── graph/               # Part 1: Neo4j schema, fixtures, writer
├── evals/               # Part 1: Accuracy, latency, calibration
├── ingestion/           # Part 1: Airbyte, OTel
├── api/                 # Part 2: FastAPI REST API
├── dashboard/           # Part 2: Next.js dashboard
├── infra/               # Terraform, K8s, Helm
├── deploy/              # Docker, Render configs
└── docs/                # Integration guides
```

---

## Specs

- **Part 1:** `Part1_Data_Intelligence_Backend_CURSOR.md`
- **Part 2:** `Part2_API_Dashboard_Deployment_Report.docx`
