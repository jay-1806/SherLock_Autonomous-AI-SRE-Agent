"""Pydantic models for graph node types."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ServiceNode(BaseModel):
    name: str
    language: Optional[str] = None
    team: Optional[str] = None
    sla_tier: Literal["tier-0", "tier-1", "tier-2", "tier-3"] = "tier-2"
    version: Optional[str] = None
    last_deploy_sha: Optional[str] = None
    last_deploy_time: Optional[datetime] = None
    last_updated_utc: datetime = Field(default_factory=datetime.utcnow)


class HostNode(BaseModel):
    instance_id: str
    hostname: Optional[str] = None
    region: str
    az: str
    instance_type: Optional[str] = None
    cpu_util: Optional[float] = None
    mem_util: Optional[float] = None
    kernel_version: Optional[str] = None
    last_updated_utc: datetime = Field(default_factory=datetime.utcnow)


class DeploymentNode(BaseModel):
    deployment_id: str
    service_name: str
    commit_sha: str
    deployer: Optional[str] = None
    timestamp: datetime
    strategy: Literal["rolling", "blue-green", "canary", "recreate"] = "rolling"
    change_diff_hash: Optional[str] = None
    rollback_available: bool = True


class IncidentNode(BaseModel):
    incident_id: str
    alert_id: Optional[str] = None
    severity: Literal["P1", "P2", "P3", "P4"]
    start_time: datetime
    resolved_time: Optional[datetime] = None
    status: Literal["active", "resolved", "false_positive"]
    root_cause_sha: Optional[str] = None
    confidence_score: Optional[float] = None
    affected_services: list[str] = Field(default_factory=list)
    embedding: Optional[list[float]] = None


class CallRelationship(BaseModel):
    from_service: str
    to_service: str
    avg_latency_ms: Optional[float] = None
    error_rate: Optional[float] = None
    p99_latency_ms: Optional[float] = None
    last_updated_utc: datetime = Field(default_factory=datetime.utcnow)
