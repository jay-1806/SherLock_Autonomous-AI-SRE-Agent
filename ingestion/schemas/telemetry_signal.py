"""Unified telemetry signal schema. All signals normalize to this before graph ingestion."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid

SignalType = Literal["metric", "log", "trace", "event"]
Severity = Literal["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]


class TelemetrySignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: SignalType
    service_name: str
    host_id: Optional[str] = None
    namespace: Optional[str] = None  # K8s namespace
    timestamp_utc: datetime
    value: Optional[float] = None  # For metrics
    body: Optional[str] = None  # For logs/events
    severity: Optional[Severity] = None
    tags: dict[str, str] = Field(default_factory=dict)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    source_connector: str  # e.g. "aws-cloudwatch", "otel-collector"
    raw_source: Optional[dict] = None  # Original payload before normalization
    pii_scrubbed: bool = False
    schema_version: str = "1.0"
