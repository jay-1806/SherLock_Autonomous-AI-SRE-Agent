"""Alert payload model — input to investigation."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AlertPayload(BaseModel):
    alert_id: Optional[str] = None
    service_name: str
    severity: str = "P2"
    description: str = ""
    fired_at: Optional[datetime] = None
    source: Optional[str] = None
    tags: dict = {}
