"""WebSocket event definitions for real-time dashboard updates."""
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel


class WebSocketEventType(str, Enum):
    """WebSocket event types broadcast to dashboard clients."""
    INVESTIGATION_CREATED = "investigation:created"
    INVESTIGATION_UPDATED = "investigation:updated"
    INVESTIGATION_COMPLETED = "investigation:completed"
    INVESTIGATION_REQUIRES_REVIEW = "investigation:requires_review"
    REMEDIATION_EXECUTED = "remediation:executed"
    SERVICE_HEALTH_CHANGED = "service:health_changed"


class WebSocketEvent(BaseModel):
    """WebSocket event payload."""
    event_type: WebSocketEventType
    investigation_id: Optional[str] = None
    data: Dict[str, Any] = {}
    timestamp: str = ""


# Rate limit: max 10 WebSocket messages per investigation per 60-second window
WS_RATE_LIMIT_PER_INVESTIGATION = 10
WS_RATE_LIMIT_WINDOW_SECONDS = 60


def create_investigation_created_event(investigation_id: str, service: str, severity: str) -> WebSocketEvent:
    """Create event when new investigation is dispatched."""
    from datetime import datetime, timezone
    return WebSocketEvent(
        event_type=WebSocketEventType.INVESTIGATION_CREATED,
        investigation_id=investigation_id,
        data={"service": service, "severity": severity, "status": "in_progress"},
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def create_investigation_completed_event(investigation_id: str, confidence: float, rca_summary: str) -> WebSocketEvent:
    """Create event when investigation is completed with results."""
    from datetime import datetime, timezone
    return WebSocketEvent(
        event_type=WebSocketEventType.INVESTIGATION_COMPLETED,
        investigation_id=investigation_id,
        data={"confidence": confidence, "rca_summary": rca_summary, "status": "resolved"},
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def create_remediation_executed_event(action_id: str, investigation_id: str, status: str) -> WebSocketEvent:
    """Create event when remediation action is executed."""
    from datetime import datetime, timezone
    return WebSocketEvent(
        event_type=WebSocketEventType.REMEDIATION_EXECUTED,
        investigation_id=investigation_id,
        data={"action_id": action_id, "execution_status": status},
        timestamp=datetime.now(timezone.utc).isoformat()
    )
