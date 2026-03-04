"""Unit tests for investigation models."""

from datetime import datetime
from agent.models.alert import AlertPayload
from agent.models.investigation import InvestigationResult, Recommendation, RootCause


def test_alert_payload():
    alert = AlertPayload(
        service_name="checkout-api",
        severity="P1",
        description="Error rate spike",
    )
    assert alert.service_name == "checkout-api"
    assert alert.severity == "P1"


def test_investigation_result_minimal():
    result = InvestigationResult(
        status="completed",
        confidence_score=0.85,
    )
    assert result.investigation_id
    assert result.schema_version == "1.0"
    assert result.status == "completed"
    assert result.confidence_score == 0.85


def test_recommendation():
    rec = Recommendation(
        rank=1,
        action="Roll back deployment",
        rationale="Deploy-induced incident",
        estimated_impact="high",
        estimated_risk="low",
        reversible=True,
    )
    assert rec.rank == 1
    assert rec.reversible is True
