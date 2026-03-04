"""Investigation data models."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class InvestigationStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class InvestigationSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimelineEvent(BaseModel):
    timestamp: str
    event: str
    source: str


class Investigation(BaseModel):
    id: str
    title: str
    description: str
    status: InvestigationStatus
    severity: InvestigationSeverity
    service: str
    created_at: str
    updated_at: str
    assigned_to: Optional[str] = None
    timeline: Optional[List[TimelineEvent]] = None
    root_cause: Optional[str] = None
    remediation: Optional[str] = None


class InvestigationSummary(BaseModel):
    id: str
    title: str
    status: InvestigationStatus
    severity: InvestigationSeverity
    service: str
    created_at: str
    confidence: Optional[float] = None
    rca_summary: Optional[str] = None
