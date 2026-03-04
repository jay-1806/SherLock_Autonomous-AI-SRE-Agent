"""FastAPI app + SRE investigation agent entry point."""

import uuid
from pathlib import Path

# Load .env from project root
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
from datetime import datetime
from contextlib import asynccontextmanager

from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.graph.investigation_graph import INVESTIGATION_GRAPH
from agent.models.alert import AlertPayload

# Alert deduplication: service -> last investigation start time
_dedup_window_minutes = int(__import__("os").environ.get("AGENT_DEDUP_WINDOW_MINUTES", "5"))
_dedup_store = {}  # service_name -> datetime


def _check_dedup(service_name: str) -> bool:
    """Return True if we should dedupe (skip) this request."""
    from datetime import timedelta

    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=_dedup_window_minutes)
    last = _dedup_store.get(service_name)
    if last and last > cutoff:
        return True
    _dedup_store[service_name] = now
    return False


class InvestigateRequest(BaseModel):
    service_name: str
    severity: str = "P2"
    description: str = ""
    alert_id: Optional[str] = None
    source: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Shutdown cleanup


app = FastAPI(title="SherLock SRE Agent", version="0.1.0", lifespan=lifespan)


@app.get("/")
async def root():
    """Redirect to API docs."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs", status_code=302)


@app.post("/investigate")
async def investigate(req: InvestigateRequest):
    """Run investigation for an alert."""
    if _check_dedup(req.service_name):
        raise HTTPException(
            status_code=409,
            detail=f"Investigation for {req.service_name} already in progress or completed within last {_dedup_window_minutes} minutes",
        )
    alert = AlertPayload(
        alert_id=req.alert_id,
        service_name=req.service_name,
        severity=req.severity,
        description=req.description,
        fired_at=datetime.utcnow(),
        source=req.source,
    )

    state = {
        "alert": alert,
        "investigation_id": f"inv-{uuid.uuid4().hex[:12]}",
        "started_at": datetime.utcnow(),
        "step_timings": {},
        "hypotheses": [],
        "requires_human_review": False,
    }

    try:
        result = await INVESTIGATION_GRAPH.ainvoke(state)
        inv_result = result.get("investigation_result")
        if not inv_result:
            raise HTTPException(status_code=500, detail="Investigation failed to produce result")
        return inv_result.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
