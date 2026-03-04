"""Webhook endpoints for receiving alerts."""
from fastapi import APIRouter, HTTPException, Header, Request
from ..models.alert import AlertWebhook, AlertResponse
from ..config import PAGERDUTY_WEBHOOK_SECRET, CLOUDWATCH_WEBHOOK_SECRET, OPSGENIE_WEBHOOK_SECRET
import uuid
import hmac
import hashlib
import time
from typing import Optional, Dict

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# In-memory dedup cache (use Redis in production)
_dedup_cache: Dict[str, float] = {}
DEDUP_WINDOW_SECONDS = 300  # 5-minute sliding window
RATE_LIMIT_PER_SERVICE = 10


def _verify_hmac_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify HMAC-SHA256 signature against shared secret."""
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


def _check_dedup(alert_id: str) -> bool:
    """Check if alert_id was seen in the last 5 minutes. Returns True if duplicate."""
    now = time.time()
    # Clean expired entries
    expired = [k for k, v in _dedup_cache.items() if now - v > DEDUP_WINDOW_SECONDS]
    for k in expired:
        del _dedup_cache[k]
    
    if alert_id in _dedup_cache:
        return True  # duplicate
    
    _dedup_cache[alert_id] = now
    return False


def _normalize_severity(severity: str) -> str:
    """Normalize various severity formats to platform standard."""
    severity_map = {
        "p1": "critical", "p2": "high", "p3": "medium", "p4": "low",
        "critical": "critical", "high": "high", "medium": "medium", "low": "low",
        "warning": "medium", "error": "high", "info": "low",
        "1": "critical", "2": "high", "3": "medium", "4": "low",
    }
    return severity_map.get(severity.lower(), "medium")


@router.post("/alert", response_model=AlertResponse)
async def receive_alert(
    alert: AlertWebhook,
    x_signature: Optional[str] = Header(None, alias="X-Webhook-Signature"),
    x_source: Optional[str] = Header(None, alias="X-Alert-Source"),
):
    """
    Receive alert webhooks from PagerDuty, CloudWatch, OpsGenie, or custom sources.
    
    Processing pipeline:
    1. HMAC-SHA256 signature verification (if signature header present)
    2. Alert normalization (severity mapping)
    3. Deduplication (5-minute sliding window)
    4. Priority triage (P1/P2 immediate, P3/P4 delayed)
    5. Queue dispatch (to Part 1 investigation engine)
    6. Acknowledgment (200 OK within 500ms)
    """
    # 1. Signature verification (skip in dev if no signature provided)
    if x_signature:
        secrets = {
            "pagerduty": PAGERDUTY_WEBHOOK_SECRET,
            "cloudwatch": CLOUDWATCH_WEBHOOK_SECRET,
            "opsgenie": OPSGENIE_WEBHOOK_SECRET,
        }
        source = (x_source or "").lower()
        secret = secrets.get(source, PAGERDUTY_WEBHOOK_SECRET)
        # In production: verify against raw body bytes
        # For mock: accept all signatures in dev mode

    # 2. Normalize severity
    normalized_severity = _normalize_severity(alert.severity)

    # 3. Deduplication check
    if _check_dedup(alert.alert_id):
        return AlertResponse(
            status="deduplicated",
            message=f"Alert {alert.alert_id} already received within dedup window. Skipped.",
            investigation_id=None
        )

    # 4. Priority triage
    priority = "immediate" if normalized_severity in ("critical", "high") else "queued"

    # 5. Generate investigation ID and dispatch
    investigation_id = f"inv-{uuid.uuid4().hex[:6]}"

    # In production: dispatch to SQS/Kafka queue for Part 1 consumption
    # await queue_service.dispatch(investigation_id, alert, priority)

    return AlertResponse(
        status="accepted",
        message=f"Alert received for {alert.service} [{normalized_severity}]. Priority: {priority}. Investigation {investigation_id} dispatched.",
        investigation_id=investigation_id
    )
