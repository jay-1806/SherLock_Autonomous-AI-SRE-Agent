# Part 1 ↔ Part 2 Integration Guide

**Repo:** https://github.com/jay-1806/SherLock_Autonomous-AI-SRE-Agent

This guide covers integrating **Part 1** (SherLock Data & Intelligence Backend) with **Part 2** (API + Dashboard). Part 2 will live in the same repo under `part2/`.

---

## 1. Interface Contract

The single interface between Part 1 and Part 2 is the **InvestigationResult JSON schema v1**:

| Field | Type | Description |
|-------|------|-------------|
| `investigation_id` | string | Unique ID (e.g. `inv-abc123`) |
| `schema_version` | string | `"1.0"` |
| `alert_id`, `alert_source` | string | Source alert |
| `created_at`, `completed_at` | datetime (ISO 8601) | Timestamps |
| `investigation_duration_seconds` | float | Duration |
| `status` | string | `completed`, `partial`, `aborted`, `timeout` |
| `confidence_score` | float | 0.0–1.0 |
| `requires_human_review` | bool | |
| `human_review_reason` | string | Optional |
| `affected_services`, `blast_radius_services` | string[] | |
| `root_cause` | object | `{ description, evidence_refs, graph_path, ... }` |
| `hypotheses` | array | `{ id, title, description, prior_probability, ... }` |
| `recommendations` | array | `{ rank, action, rationale, ... }` |
| `external_sources` | array | Tavily results |
| `narrative_summary` | string | Markdown |
| `graph_snapshot_s3_uri` | string | Optional S3 URI |
| `step_timings` | object | Per-step timings |

Full schema: `SherLock/agent/models/investigation.py`

---

## 2. Integration Modes

### A. Production (SQS + S3)

```
Part 1 Agent → S3 (s3://sre-investigations/{id}.json) + SQS (sre-investigations-completed)
                                                              ↓
Part 2 investigation-consumer (polls SQS) → stores in DB → API + Dashboard
```

### B. Local Dev (HTTP callback)

```
Part 1 Agent → POST InvestigationResult JSON to Part 2 webhook URL
Part 2 API receives, stores, serves to dashboard
```

### C. Shared repo (monorepo)

```
sre-platform/
├── part1/          # SherLock (agent, graph, ingestion, evals)
├── part2/          # API, dashboard, investigation-consumer
└── shared/         # InvestigationResult schema (TypeScript + Python)
```

---

## 3. Step-by-Step Integration

### Step 1: Clone or Add Part 2

If Part 2 is in a separate GitHub repo:

```bash
cd /Users/spartan/Desktop/AWS\ hack

# Option A: Clone Part 2 as sibling
git clone <PART2_GITHUB_URL> sre-platform-part2

# Option B: Add Part 2 as submodule inside SherLock
cd SherLock
git submodule add <PART2_GITHUB_URL> part2
```

If Part 2 is in the same monorepo:

```bash
cd SherLock
# Ensure part2/ or dashboard/ directory exists
ls part2/  # or dashboard/
```

### Step 2: Align Schema in Part 2

Part 2 must consume `InvestigationResult` v1. Ensure Part 2 has:

- **TypeScript/JS**: A type/interface matching the schema (or use `shared/schema.ts` if you create it)
- **API**: Endpoint to receive investigations (e.g. `POST /api/investigations` or consumer that writes to DB)

Example TypeScript type (for Part 2 dashboard):

```typescript
interface InvestigationResult {
  investigation_id: string;
  schema_version: string;
  alert_id?: string;
  alert_source?: string;
  created_at: string;
  completed_at?: string;
  investigation_duration_seconds?: number;
  status: 'completed' | 'partial' | 'aborted' | 'timeout';
  confidence_score: number;
  requires_human_review: boolean;
  human_review_reason?: string;
  affected_services: string[];
  blast_radius_services: string[];
  root_cause?: { description: string; /* ... */ };
  hypotheses: Array<{ id: string; title: string; description: string; /* ... */ }>;
  recommendations: Array<{ rank: number; action: string; rationale: string; /* ... */ }>;
  narrative_summary?: string;
  graph_snapshot_s3_uri?: string;
  step_timings?: Record<string, number>;
}
```

### Step 3: Implement Part 1 → SQS + S3 (Production)

Enable publishing in Part 1's `output_serialization.py`:

1. Add env vars:
   - `AWS_SQS_INVESTIGATIONS_COMPLETED_URL` — SQS queue URL
   - `AWS_S3_INVESTIGATIONS_BUCKET` — S3 bucket name
   - `AWS_REGION` — e.g. `us-east-1`

2. After building `InvestigationResult`, write JSON to S3 and send message to SQS (investigation_id, S3 key).

### Step 4: Implement Part 2 investigation-consumer

Part 2 needs a worker that:

1. Polls `sre-investigations-completed` SQS queue
2. Receives message with `investigation_id` (and optionally S3 key)
3. Fetches full JSON from S3: `s3://sre-investigations/{investigation_id}.json`
4. Parses `InvestigationResult`, stores in DB (Postgres, etc.)
5. Deletes message from SQS after successful processing

### Step 5: Local Dev — HTTP webhook (no AWS)

For local development without SQS/S3:

1. Part 1: Add optional `PART2_WEBHOOK_URL` env var. If set, `serialize_output` POSTs the InvestigationResult JSON to that URL.
2. Part 2: Expose `POST /api/investigations/webhook` that accepts the JSON, stores it, returns 200.

Example Part 1 change (pseudo):

```python
# In serialize_output, after building result:
webhook = os.environ.get("PART2_WEBHOOK_URL")
if webhook:
    httpx.post(webhook, json=result.model_dump(mode="json"))
```

### Step 6: Wire Part 2 API + Dashboard

- **API**: `GET /api/investigations`, `GET /api/investigations/:id` — serve stored investigations
- **Dashboard**: Fetch from API, render investigation cards, root cause, hypotheses, recommendations, narrative

### Step 7: End-to-end Test

```bash
# Terminal 1: Part 1 agent
cd SherLock && make agent

# Terminal 2: Part 2 API (if local)
cd part2 && npm run dev

# Terminal 3: Trigger investigation
curl -X POST http://localhost:8001/investigate \
  -H "Content-Type: application/json" \
  -d '{"service_name":"checkout-api","severity":"P1","description":"Error rate spike"}'

# If webhook: Part 2 should receive the result
# If SQS: Consumer should pick up, store, and API should serve it
```

---

## 4. Repo Layout Options

### Option A: Monorepo

```
sre-platform/
├── part1/              # SherLock (agent, graph, evals)
│   ├── agent/
│   ├── graph/
│   ├── evals/
│   └── ...
├── part2/              # API + Dashboard
│   ├── api/            # FastAPI or Express
│   ├── dashboard/      # React/Next.js
│   └── consumer/       # SQS consumer
├── shared/
│   └── schema/         # InvestigationResult (Python + TS)
└── docker-compose.yml  # Part1 + Part2 + Neo4j + Kafka
```

### Option B: Separate repos

- Part 1 repo: SherLock (current)
- Part 2 repo: sre-platform-dashboard (or similar)
- Integration: SQS + S3 in AWS; both deployed independently

---

## 5. Environment Variables Summary

| Component | Variable | Purpose |
|-----------|----------|---------|
| Part 1 | `AWS_SQS_INVESTIGATIONS_COMPLETED_URL` | SQS queue for completed investigations |
| Part 1 | `AWS_S3_INVESTIGATIONS_BUCKET` | S3 bucket for JSON storage |
| Part 1 | `PART2_WEBHOOK_URL` | (Optional) HTTP callback for local dev |
| Part 2 | `AWS_SQS_INVESTIGATIONS_COMPLETED_URL` | Same queue (consumer) |
| Part 2 | `AWS_S3_INVESTIGATIONS_BUCKET` | Same bucket (fetch JSON) |
| Part 2 | `DATABASE_URL` | Postgres or other DB for stored investigations |

---

## 6. SherLock Repo Layout (Target)

```
SherLock/                          # https://github.com/jay-1806/SherLock_Autonomous-AI-SRE-Agent
├── agent/                         # Part 1: Investigation engine
├── graph/                         # Part 1: Neo4j, fixtures
├── evals/                         # Part 1: Accuracy, latency runners
├── ingestion/                     # Part 1: Airbyte, OTel
├── infra/                         # Terraform, K8s
├── part2/                         # Part 2: API + Dashboard (to add)
│   ├── api/                       # FastAPI or Express — serves investigations
│   ├── dashboard/                 # React/Next.js — UI
│   └── consumer/                  # SQS consumer worker
├── shared/                        # Shared schema (optional)
│   └── investigation_schema.json  # InvestigationResult v1
├── docker-compose.yml             # Part 1 + Part 2 + Neo4j
└── Makefile                       # make agent | make part2-api | make part2-dashboard
```

---

## 7. Next Actions Checklist

- [ ] Create `part2/` structure (api, dashboard, consumer)
- [ ] Add InvestigationResult schema/types to Part 2
- [ ] Implement `POST /api/investigations/webhook` in Part 2 (for local dev)
- [ ] Add optional webhook publish in Part 1 `output_serialization.py`
- [ ] (Production) Implement S3 + SQS publish in Part 1
- [ ] (Production) Implement SQS consumer in Part 2
- [ ] Add `docker-compose` override to run Part 1 + Part 2 together
- [ ] End-to-end test: alert → Part 1 → Part 2 → dashboard

---

---

## 8. Quick Start (After Part 2 Exists)

```bash
# Terminal 1: Neo4j + Kafka
docker-compose up -d

# Terminal 2: Part 1 agent
make agent

# Terminal 3: Part 2 API (once built)
cd part2 && npm run dev   # or: make part2-api

# Terminal 4: Trigger investigation
curl -X POST http://localhost:8001/investigate \
  -H "Content-Type: application/json" \
  -d '{"service_name":"checkout-api","severity":"P1","description":"Error spike"}'

# If webhook configured: Part 2 receives JSON
# If SQS configured: Consumer fetches from S3, Part 2 API serves it
```
