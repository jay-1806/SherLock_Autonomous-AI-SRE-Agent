"""PII scrubbing for telemetry signals before graph ingestion."""

import re
import hashlib
from typing import Any

PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r"\b(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "ssn": re.compile(r"\b\d{3}[-]?\d{2}[-]?\d{4}\b"),
    "aws_key": re.compile(r"(AKIA|ASIA)[A-Z0-9]{16}"),
    "jwt": re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
    "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

PII_FIELD_NAMES = {"user_id", "email", "username", "customer_id", "session_id", "token"}


def scrub_signal(signal: dict[str, Any]) -> dict[str, Any]:
    """Remove or hash PII from a telemetry signal before graph ingestion."""
    scrubbed = signal.copy()

    # Hash known PII fields
    if "tags" in scrubbed and isinstance(scrubbed["tags"], dict):
        for field in PII_FIELD_NAMES:
            if field in scrubbed["tags"]:
                scrubbed["tags"][field] = _hash_value(str(scrubbed["tags"][field]))

    # Regex-scrub log body
    if body := scrubbed.get("body"):
        for pii_type, pattern in PII_PATTERNS.items():
            body = pattern.sub(f"[{pii_type.upper()}_REDACTED]", body)
        scrubbed["body"] = body

    scrubbed["pii_scrubbed"] = True
    return scrubbed


def _hash_value(value: str) -> str:
    return f"[HASHED:{hashlib.sha256(value.encode()).hexdigest()[:12]}]"
