"""Investigation endpoints."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models.investigation import Investigation, InvestigationSummary

router = APIRouter(prefix="/investigations", tags=["investigations"])


@router.get("", response_model=List[InvestigationSummary])
async def list_investigations(
    status: Optional[str] = Query(None, description="Filter by status: open, in_progress, resolved, closed"),
    severity: Optional[str] = Query(None, description="Filter by severity: low, medium, high, critical"),
    service: Optional[str] = Query(None, description="Filter by service name"),
):
    """
    List investigations with optional filters.
    
    Supports filtering by status, severity, and service name.
    Returns summary view with confidence scores.
    """
    from ..services.mock_data import get_all_investigations
    
    results = get_all_investigations()
    
    if status:
        results = [r for r in results if r["status"] == status]
    if severity:
        results = [r for r in results if r["severity"] == severity]
    if service:
        results = [r for r in results if r["service"] == service]
    
    return results


@router.get("/{investigation_id}")
async def get_investigation(investigation_id: str):
    """
    Retrieve full investigation JSON object by ID.
    
    Returns complete investigation including hypotheses, evidence,
    timeline, blast radius, and NBA recommendations.
    """
    from ..services.mock_data import get_investigation_by_id
    
    investigation = get_investigation_by_id(investigation_id)
    if not investigation:
        raise HTTPException(
            status_code=404,
            detail=f"Investigation {investigation_id} not found"
        )
    return investigation


@router.get("/{investigation_id}/graph")
async def get_investigation_graph(investigation_id: str):
    """
    Return graph topology data for visualization.
    
    Returns nodes (services, hosts, deployments, incidents) and edges
    (dependencies with call volume and error rates) for Neovis.js rendering.
    """
    from ..services.mock_data import get_investigation_graph
    
    graph = get_investigation_graph(investigation_id)
    if not graph:
        raise HTTPException(
            status_code=404,
            detail=f"Investigation {investigation_id} not found"
        )
    return graph
