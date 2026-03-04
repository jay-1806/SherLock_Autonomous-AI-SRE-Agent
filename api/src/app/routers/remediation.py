"""Remediation catalog and execution endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/remediation", tags=["remediation"])


class ExecuteRequest(BaseModel):
    investigation_id: str
    dry_run: bool = False
    mfa_token: Optional[str] = None


class ExecuteResponse(BaseModel):
    execution_id: str
    action_id: str
    action_name: str
    status: str
    message: str
    dry_run: bool


@router.get("/catalog")
async def get_catalog():
    """
    List all pre-approved auto-remediation actions with metadata.
    
    Returns the full remediation action catalog including risk levels,
    trigger conditions, and execution history.
    """
    from ..services.mock_data import get_remediation_catalog
    return get_remediation_catalog()


@router.get("/catalog/{action_id}")
async def get_action(action_id: str):
    """Get a single remediation action by ID."""
    from ..services.mock_data import get_remediation_action
    action = get_remediation_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
    return action


@router.get("/executions")
async def get_executions():
    """
    Get the remediation execution audit log.
    
    Returns history of all executed remediation actions with pre/post state.
    """
    from ..services.mock_data import get_execution_log
    return get_execution_log()


@router.post("/{action_id}/execute", response_model=ExecuteResponse)
async def execute_action(action_id: str, request: ExecuteRequest):
    """
    Execute a pre-approved remediation action.
    
    Safety controls:
    - Medium/High risk actions require MFA token
    - Dry-run mode available for testing
    - Pre-execution confidence check against investigation
    - Blast radius validation (max 3 services)
    """
    from ..services.mock_data import get_remediation_action, get_investigation_by_id

    action = get_remediation_action(action_id)
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found in catalog")

    # MFA check for medium/high risk actions
    if action["requires_mfa"] and not request.mfa_token:
        raise HTTPException(
            status_code=403,
            detail=f"Action '{action_id}' requires MFA token. Risk level: {action['risk_level']}"
        )

    # Validate investigation exists
    investigation = get_investigation_by_id(request.investigation_id)
    if not investigation:
        raise HTTPException(status_code=404, detail=f"Investigation '{request.investigation_id}' not found")

    # Pre-execution confidence check
    confidence = investigation.get("confidence", 0)
    if confidence < 0.85 and action["risk_level"] in ("medium", "high"):
        raise HTTPException(
            status_code=422,
            detail=f"Investigation confidence ({confidence:.0%}) below threshold for {action['risk_level']}-risk action. Minimum: 85%"
        )

    # Blast radius check
    blast_radius = investigation.get("blast_radius", [])
    if len(blast_radius) > 3 and not request.dry_run:
        raise HTTPException(
            status_code=422,
            detail=f"Blast radius ({len(blast_radius)} services) exceeds limit of 3. Manual override required."
        )

    execution_id = f"exec-{uuid.uuid4().hex[:6]}"

    if request.dry_run:
        return ExecuteResponse(
            execution_id=execution_id,
            action_id=action_id,
            action_name=action["name"],
            status="dry_run_complete",
            message=f"DRY RUN: Would execute '{action['name']}' for investigation {request.investigation_id}. Estimated duration: {action['estimated_duration']}",
            dry_run=True
        )

    return ExecuteResponse(
        execution_id=execution_id,
        action_id=action_id,
        action_name=action["name"],
        status="executed",
        message=f"Successfully executed '{action['name']}' for investigation {request.investigation_id}. Duration: {action['estimated_duration']}",
        dry_run=False
    )
