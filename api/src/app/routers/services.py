"""Service endpoints."""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/services", tags=["services"])


@router.get("")
async def list_services():
    """
    List all services with health status.
    
    Returns service name, status, health score, SLA tier, and active incident count.
    """
    from ..services.mock_data import get_all_services
    return get_all_services()


@router.get("/{service_name}")
async def get_service(service_name: str):
    """
    Get full details for a specific service by name.
    """
    from ..services.mock_data import get_service_by_name
    service = get_service_by_name(service_name)
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    return service


@router.get("/{service_name}/history")
async def get_service_history(service_name: str):
    """
    Return incident history and RCA trend for a specific service.
    """
    from ..services.mock_data import get_service_by_name
    service = get_service_by_name(service_name)
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    return {
        "service": service_name,
        "display_name": service["display_name"],
        "incident_history": service.get("incident_history", []),
        "total_incidents_30d": len(service.get("incident_history", [])),
        "dependencies": service.get("dependencies", []),
    }
