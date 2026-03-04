"""Unit tests for TelemetrySignal schema."""

from datetime import datetime
import pytest
from ingestion.schemas.telemetry_signal import TelemetrySignal


def test_telemetry_signal_minimal():
    s = TelemetrySignal(
        signal_type="metric",
        service_name="checkout-api",
        timestamp_utc=datetime.utcnow(),
        source_connector="aws-cloudwatch",
    )
    assert s.service_name == "checkout-api"
    assert s.schema_version == "1.0"
    assert s.signal_id  # auto-generated


def test_telemetry_signal_full():
    s = TelemetrySignal(
        signal_type="log",
        service_name="api",
        timestamp_utc=datetime.utcnow(),
        source_connector="otel",
        body="Error: connection refused",
        severity="ERROR",
        tags={"trace_id": "abc123"},
    )
    assert s.body == "Error: connection refused"
    assert s.severity == "ERROR"
    assert s.tags["trace_id"] == "abc123"
