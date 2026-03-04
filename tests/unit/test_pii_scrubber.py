"""Unit tests for PII scrubber."""

import pytest
from ingestion.airbyte.pii_scrubber import scrub_signal


def test_scrub_email():
    sig = {"body": "Contact user@example.com for help", "tags": {}}
    out = scrub_signal(sig)
    assert "EMAIL_REDACTED" in out["body"]
    assert "user@example.com" not in out["body"]
    assert out["pii_scrubbed"] is True


def test_scrub_aws_key():
    sig = {"body": "Key AKIAIOSFODNN7EXAMPLE found", "tags": {}}
    out = scrub_signal(sig)
    assert "AWS_KEY" in str(out["body"]).upper() or "REDACTED" in out["body"]
    assert out["pii_scrubbed"] is True


def test_hash_pii_field():
    sig = {"tags": {"user_id": "alice123"}}
    out = scrub_signal(sig)
    assert out["tags"]["user_id"].startswith("[HASHED:")
    assert "alice123" not in out["tags"]["user_id"]
