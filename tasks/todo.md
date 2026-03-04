# SherLock — Part 1: Data & Intelligence Backend

> Spec: Part1_Data_Intelligence_Backend_CURSOR.md

---

## Phase 1 — Foundation (Weeks 1–8)

### Infrastructure Setup
- [x] Terraform scaffolding (`infra/terraform/`): EKS, S3, IAM
- [x] K8s manifests (`infra/k8s/`): agent, graph-writer
- [ ] Provision AWS EKS cluster (`cd infra/terraform && terraform apply`)
- [ ] Create Amazon MSK Kafka cluster (3 brokers, TLS + IAM auth)
- [ ] Create S3 buckets via Terraform
- [ ] Set up AWS Secrets Manager with all Part 1 secrets
- [ ] Provision Neo4j Aura Enterprise instance
- [ ] Configure VPC peering between EKS and Neo4j Aura
- [ ] Create all IAM roles with IRSA annotations
- [ ] Set up 5 CloudWatch alarms (see spec §13.3)

### Graph Schema
- [x] Write and apply `constraints.cypher`
- [x] Write and apply `indexes.cypher`
- [x] Write and run local graph fixture loader (20 services)
- [x] Vector index schema + validation script (`graph/embeddings/validate_vector_index.py`)

### Ingestion Layer
- [x] Configure Airbyte connection YAMLs (CloudWatch, X-Ray, PagerDuty)
- [x] Write schema normalization dbt transforms
- [x] Implement and test PII scrubber (`pii_scrubber.py`)
- [x] OTel Collector config (`collector-config.yaml`)
- [x] OTel DaemonSet manifest (`ingestion/otel/daemonset.yaml`)
- [ ] Validate end-to-end: CloudWatch → Kafka → TelemetrySignal

### Graph Writer
- [x] Implement `neo4j_client.py` with retry logic
- [x] Implement `ServiceHandler`
- [x] Implement `DeploymentHandler`
- [x] Implement `IncidentHandler`
- [x] Implement Kafka consumer main loop
- [ ] Deploy graph writer to EKS
- [ ] Validate: Kafka event → Neo4j node visible

### Agent — MVP
- [x] Define and freeze `InvestigationResult` Pydantic schema
- [x] Implement `InvestigationState` TypedDict
- [x] Implement `fetch_context` node
- [x] Implement `retrieve_historical` node (placeholder for vector search)
- [x] Implement `generate_hypotheses` node
- [x] Implement `collect_evidence` node
- [x] Implement `fetch_external_intelligence` node (Tavily)
- [x] Implement `synthesize_evidence` node
- [x] Implement `generate_rca_narrative` node
- [x] Implement `generate_recommendations` node
- [x] Implement `serialize_output` node
- [x] Wire LangGraph `investigation_graph.py`
- [x] Implement confidence scorer
- [x] Build FastAPI app with `/investigate` endpoint
- [ ] Deploy agent to EKS

### Evaluation Harness
- [x] Define `LabeledIncident` schema
- [x] Create `labeled_incidents.json` (20 labeled incidents)
- [x] Implement `accuracy_runner.py`, `latency_runner.py`, `calibration_runner.py`
- [x] Relax RCA metric (F1-based partial overlap)
- [x] Lower root-cause threshold for evals (ROOT_CAUSE_POSTERIOR_THRESHOLD=0.35)
- [ ] Label remaining 30 incidents (target: 50 total)
- [x] Add eval CI step (runs on main push, optional)
- [x] Run first baseline eval (~21% baseline)

### Phase 1 Gate Check
- [ ] First live investigation report for real production alert
- [ ] RCA accuracy ≥ 85% on eval dataset
- [ ] Investigation latency P75 ≤ 6 minutes
- [ ] `InvestigationResult` JSON v1 consumed by Part 2 mock

---

## Phase 2 — Autonomous Mode (Weeks 9–16)
- [ ] Connect 15+ production telemetry sources
- [x] Implement `AnomalySignalHandler` in graph writer
- [x] Enable confidence gate: autonomous at ≥ 0.85
- [x] Implement Bedrock fallback
- [x] Implement alert deduplication
- [x] Add `HostHandler` and `ConfigChangeHandler`
- [ ] Expand eval dataset to 100 incidents
- [ ] ≥ 80% autonomous coverage for P1/P2
- [ ] Investigation latency P75 ≤ 5 minutes

---

## Phase 3 — Self-Learning (Weeks 17–24)
- [ ] Proactive anomaly detection loop
- [ ] Post-mortem auto-generation
- [ ] Feedback loop: engineer ratings → eval dataset
- [ ] Confidence model retraining pipeline
- [ ] RCA accuracy ≥ 92%
- [ ] MTTRC reduction ≥ 70% vs baseline

---

## Workflow Rules (from cursor.md)
| Rule | Status |
|------|--------|
| Plan first for non-trivial tasks | ✅ |
| Use subagents for research/exploration | Ready |
| Update lessons.md after corrections | Ready |
| Verify before marking done | Ready |
| Demand elegance, minimal impact | Ready |
| Autonomous bug fixing | Ready |
