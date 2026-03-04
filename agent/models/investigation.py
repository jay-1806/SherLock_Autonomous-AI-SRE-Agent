"""InvestigationResult — THE interface contract with Part 2. Never break without versioning."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid


class EvidenceRef(BaseModel):
    source: Literal["neo4j", "telemetry", "tavily"]
    description: str
    cypher_query: Optional[str] = None
    result_summary: str = ""
    confidence_contribution: float = 0.0


class GraphPathStep(BaseModel):
    node_label: str
    node_name: str
    relationship: Optional[str] = None
    properties: dict = Field(default_factory=dict)


class RootCause(BaseModel):
    description: str
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)
    graph_path: list[GraphPathStep] = Field(default_factory=list)
    contributing_factors: list[str] = Field(default_factory=list)
    deployment_sha: Optional[str] = None
    timeline_minutes_before_alert: Optional[int] = None


class HypothesisOutput(BaseModel):
    id: str
    title: str
    description: str
    prior_probability: float
    posterior_probability: Optional[float] = None
    status: Literal["confirmed", "ruled_out", "insufficient_evidence", "pending"]
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)


class Recommendation(BaseModel):
    rank: int
    action: str
    action_catalog_id: Optional[str] = None
    rationale: str
    estimated_impact: Literal["high", "medium", "low"]
    estimated_risk: Literal["high", "medium", "low"]
    reversible: bool
    estimated_time_minutes: Optional[int] = None


class InvestigationResult(BaseModel):
    investigation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: str = "1.0"
    alert_id: Optional[str] = None
    alert_source: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    investigation_duration_seconds: Optional[float] = None
    status: Literal["completed", "partial", "aborted", "timeout"]
    confidence_score: float = 0.0
    requires_human_review: bool = False
    human_review_reason: Optional[str] = None
    affected_services: list[str] = Field(default_factory=list)
    blast_radius_services: list[str] = Field(default_factory=list)
    root_cause: Optional[RootCause] = None
    hypotheses: list[HypothesisOutput] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    external_sources: list[dict] = Field(default_factory=list)
    graph_snapshot_s3_uri: Optional[str] = None
    narrative_summary: Optional[str] = None
    step_timings: dict[str, float] = Field(default_factory=dict)
