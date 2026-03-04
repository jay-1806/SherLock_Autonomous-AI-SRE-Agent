"""Labeled incident schema for eval dataset."""

from pydantic import BaseModel
from typing import Optional


class LabeledIncident(BaseModel):
    incident_id: str
    alert_payload: dict
    ground_truth_root_cause: str
    ground_truth_affected_services: list[str]
    ground_truth_deployment_sha: Optional[str] = None
    ground_truth_recommendations: list[str]
    difficulty: str  # easy | medium | hard
    incident_category: str  # deploy-induced | config-drift | dependency-failure | ...
    labeled_by: str
    labeled_at: str
    notes: Optional[str] = None
