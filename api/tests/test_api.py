"""
SherLock API — Comprehensive Test Suite
Tests all 16 endpoints with status codes, response shapes, and edge cases.
"""
import pytest
from fastapi.testclient import TestClient
from src.app.main import app


client = TestClient(app)


# ─── Root & Health ───────────────────────────────────────────────────────────


class TestRoot:
    def test_root_returns_api_info(self):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "SherLock SRE Platform API"
        assert "version" in data
        assert "endpoints" in data

    def test_health_check(self):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "subsystems" in data


# ─── Investigations ─────────────────────────────────────────────────────────


class TestInvestigations:
    def test_list_investigations(self):
        r = client.get("/investigations")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 6  # mock data has 6 investigations

    def test_list_investigations_filter_by_status(self):
        r = client.get("/investigations?status=open")
        assert r.status_code == 200
        data = r.json()
        assert all(inv["status"] == "open" for inv in data)

    def test_list_investigations_filter_by_severity(self):
        r = client.get("/investigations?severity=critical")
        assert r.status_code == 200
        data = r.json()
        assert all(inv["severity"] == "critical" for inv in data)

    def test_get_investigation_by_id(self):
        r = client.get("/investigations/inv-001")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == "inv-001"
        assert data["title"] == "API Gateway High Latency"
        assert "hypotheses" in data
        assert "evidence" in data
        assert "timeline" in data
        assert "blast_radius" in data
        assert data["confidence"] == 0.87

    def test_get_investigation_not_found(self):
        r = client.get("/investigations/inv-999")
        assert r.status_code == 404

    def test_investigation_has_confidence(self):
        """Verify confidence field is included in list responses."""
        r = client.get("/investigations")
        data = r.json()
        investigations_with_confidence = [
            inv for inv in data if inv.get("confidence") is not None
        ]
        assert len(investigations_with_confidence) > 0

    def test_get_investigation_graph(self):
        r = client.get("/investigations/inv-001/graph")
        assert r.status_code == 200
        data = r.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) > 0
        assert len(data["edges"]) > 0

    def test_get_investigation_graph_not_found(self):
        r = client.get("/investigations/inv-999/graph")
        assert r.status_code == 404


# ─── Services ────────────────────────────────────────────────────────────────


class TestServices:
    def test_list_services(self):
        r = client.get("/services")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 8  # mock data has 8 services

    def test_service_has_health_fields(self):
        r = client.get("/services")
        data = r.json()
        for svc in data:
            assert "name" in svc
            assert "status" in svc
            assert "health_score" in svc
            assert "sla_tier" in svc

    def test_get_service_detail(self):
        r = client.get("/services/api-gateway")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "api-gateway"

    def test_get_service_not_found(self):
        r = client.get("/services/nonexistent-service")
        assert r.status_code == 404

    def test_get_service_history(self):
        r = client.get("/services/api-gateway/history")
        assert r.status_code == 200
        data = r.json()
        assert data["service"] == "api-gateway"
        assert "display_name" in data
        assert "incident_history" in data


# ─── Remediation ─────────────────────────────────────────────────────────────


class TestRemediation:
    def test_get_catalog(self):
        r = client.get("/remediation/catalog")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 8  # 8 remediation actions

    def test_catalog_action_shape(self):
        r = client.get("/remediation/catalog")
        data = r.json()
        action = data[0]
        assert "action_id" in action
        assert "name" in action
        assert "risk_level" in action
        assert "category" in action

    def test_get_single_action(self):
        r = client.get("/remediation/catalog/ACT-001")
        assert r.status_code == 200
        data = r.json()
        assert data["action_id"] == "ACT-001"

    def test_get_action_not_found(self):
        r = client.get("/remediation/catalog/ACT-999")
        assert r.status_code == 404

    def test_get_execution_log(self):
        r = client.get("/remediation/executions")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_execute_action_low_risk(self):
        """Low-risk action should execute without MFA."""
        r = client.post(
            "/remediation/ACT-001/execute",
            json={"investigation_id": "inv-001", "executed_by": "test-user"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "executed"
        assert "execution_id" in data

    def test_execute_action_high_risk_requires_mfa(self):
        """Medium/high-risk action should require MFA token."""
        r = client.post(
            "/remediation/ACT-004/execute",
            json={"investigation_id": "inv-001", "executed_by": "test-user"},
        )
        # ACT-004 is medium risk with requires_mfa=True, no MFA token provided
        assert r.status_code == 403


# ─── Evals / KPIs ───────────────────────────────────────────────────────────


class TestEvals:
    def test_get_eval_summary(self):
        r = client.get("/evals/summary")
        assert r.status_code == 200
        data = r.json()
        assert "kpis" in data
        assert "summary_stats" in data

    def test_eval_metrics_shape(self):
        r = client.get("/evals/summary")
        data = r.json()
        kpis = data["kpis"]
        assert isinstance(kpis, list)
        assert len(kpis) > 0
        kpi = kpis[0]
        assert "name" in kpi
        assert "value" in kpi
        assert "target" in kpi
        assert "status" in kpi


# ─── Feedback ────────────────────────────────────────────────────────────────


class TestFeedback:
    def test_list_feedback(self):
        r = client.get("/feedback")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_feedback_entry_shape(self):
        r = client.get("/feedback")
        data = r.json()
        entry = data[0]
        assert "investigation_id" in entry
        assert "rating" in entry
        assert "submitted_by" in entry

    def test_submit_feedback(self):
        r = client.post(
            "/feedback/inv-001",
            json={
                "rating": "correct",
                "comment": "AI nailed the root cause",
                "submitted_by": "test-engineer",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "accepted"


# ─── Webhooks ────────────────────────────────────────────────────────────────


class TestWebhooks:
    def test_receive_alert(self):
        r = client.post(
            "/webhooks/alert",
            json={
                "source": "datadog",
                "alert_id": "test-alert-pytest",
                "service": "api-gateway",
                "severity": "high",
                "description": "High CPU utilization on api-gateway",
                "timestamp": "2026-02-27T10:00:00Z",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "investigation_id" in data
        assert data["status"] == "accepted"


# ─── Metrics ─────────────────────────────────────────────────────────────────


class TestMetrics:
    def test_prometheus_metrics(self):
        r = client.get("/metrics")
        assert r.status_code == 200
        # Metrics are returned as plain text (Prometheus format)
        assert "http_requests_total" in r.text or "investigation" in r.text
