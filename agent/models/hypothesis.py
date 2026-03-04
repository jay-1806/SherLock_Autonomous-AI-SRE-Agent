"""Hypothesis model for investigation state."""

from pydantic import BaseModel
from typing import Optional, Literal


class Hypothesis(BaseModel):
    id: str
    title: str
    description: str
    prior_probability: float
    posterior_probability: Optional[float] = None
    status: Literal["confirmed", "ruled_out", "insufficient_evidence", "pending"] = "pending"
    evidence_refs: list = []
    confirming_evidence_queries: list[str] = []
    denying_evidence_queries: list[str] = []
    relevant_services: list[str] = []
    relevant_deployment_sha: Optional[str] = None
