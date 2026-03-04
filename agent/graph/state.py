"""Investigation state — LangGraph TypedDict."""

from typing import TypedDict, Optional, Annotated
from datetime import datetime
import operator

from agent.models.alert import AlertPayload
from agent.models.hypothesis import Hypothesis
from agent.models.investigation import InvestigationResult


class InvestigationState(TypedDict):
    alert: AlertPayload
    investigation_id: str
    started_at: datetime
    affected_service_context: Optional[dict]
    deployment_history: Optional[list]
    similar_incidents: Optional[list]
    hypotheses: Annotated[list[Hypothesis], operator.add]
    evidence_by_hypothesis: Optional[dict]
    external_sources: Optional[list]
    ranked_conclusions: Optional[list]
    root_cause: Optional[dict]
    recommendations: Optional[list]
    confidence_score: Optional[float]
    narrative_summary: Optional[str]
    investigation_result: Optional[InvestigationResult]
    error: Optional[str]
    requires_human_review: bool
    step_timings: dict
