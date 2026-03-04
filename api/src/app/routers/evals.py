"""Eval summary and KPI endpoints."""
from fastapi import APIRouter

router = APIRouter(tags=["evals"])


@router.get("/evals/summary")
async def get_eval_summary():
    """
    Return latest eval accuracy scores and KPI trends.
    
    Includes all 8 platform KPIs with current values, targets,
    trends, and 6-month history for sparkline visualization.
    """
    from ..services.mock_data import get_eval_summary
    return get_eval_summary()
