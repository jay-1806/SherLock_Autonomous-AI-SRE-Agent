"""Alert data models."""
from pydantic import BaseModel
from typing import Optional, Dict, Any


class AlertWebhook(BaseModel):
    alert_id: str
    service: str
    severity: str
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AlertResponse(BaseModel):
    status: str
    message: str
    investigation_id: Optional[str] = None
