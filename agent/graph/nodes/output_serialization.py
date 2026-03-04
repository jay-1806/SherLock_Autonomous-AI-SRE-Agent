"""Step 9: JSON output + S3 + SQS publish."""

import time
import uuid
from datetime import datetime
from agent.graph.state import InvestigationState
from agent.models.investigation import (
    InvestigationResult,
    RootCause,
    HypothesisOutput,
    EvidenceRef,
)


async def serialize_output(state: InvestigationState) -> dict:
    start = time.time()
    alert = state["alert"]
    inv_id = state.get("investigation_id", str(uuid.uuid4()))
    started = state.get("started_at", datetime.utcnow())
    step_timings = state.get("step_timings", {})

    root_cause = state.get("root_cause")
    rc_out = None
    if root_cause:
        rc_out = RootCause(
            description=root_cause.get("description", ""),
            evidence_refs=[],
            graph_path=[],
            contributing_factors=[],
        )

    hypotheses_out = []
    for h in state.get("hypotheses", []):
        hypotheses_out.append(
            HypothesisOutput(
                id=h.id,
                title=h.title,
                description=h.description,
                prior_probability=h.prior_probability,
                posterior_probability=h.posterior_probability,
                status=h.status,
                evidence_refs=[],
            )
        )

    completed = datetime.utcnow()
    duration = (completed - started).total_seconds() if isinstance(started, datetime) else 0

    confidence = state.get("confidence_score", 0.0)
    auto_thresh = float(__import__("os").environ.get("AGENT_CONFIDENCE_AUTONOMOUS_THRESHOLD", "0.85"))
    medium_thresh = float(__import__("os").environ.get("AGENT_CONFIDENCE_MEDIUM_THRESHOLD", "0.60"))
    requires_review = confidence < auto_thresh
    human_reason = None
    if confidence < medium_thresh:
        human_reason = "Low confidence; manual triage required"
    elif confidence < auto_thresh:
        human_reason = "Below autonomous threshold; recommend human verification"

    result = InvestigationResult(
        investigation_id=inv_id,
        schema_version="1.0",
        alert_id=alert.alert_id,
        alert_source=alert.source,
        created_at=started,
        completed_at=completed,
        investigation_duration_seconds=duration,
        status="completed",
        confidence_score=confidence,
        requires_human_review=requires_review,
        human_review_reason=human_reason,
        affected_services=[alert.service_name],
        blast_radius_services=[],
        root_cause=rc_out,
        hypotheses=hypotheses_out,
        recommendations=state.get("recommendations", []),
        external_sources=state.get("external_sources", []),
        narrative_summary=state.get("narrative_summary"),
        step_timings={**step_timings, "serialize_output": time.time() - start},
    )

    # TODO: Publish to S3 + SQS in production
    return {
        "investigation_result": result,
        "step_timings": {**step_timings, "serialize_output": time.time() - start},
    }
