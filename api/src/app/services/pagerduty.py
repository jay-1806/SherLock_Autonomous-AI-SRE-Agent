"""PagerDuty enrichment service."""
from typing import Dict, Any
from ..config import PAGERDUTY_API_KEY


async def enrich_pagerduty_incident(
    pagerduty_incident_id: str,
    investigation: Dict[str, Any]
) -> bool:
    """
    Write investigation result back to PagerDuty incident as a note.
    
    Enriches the PagerDuty timeline with structured RCA context, keeping
    PagerDuty as the single source of truth for incident responders.
    
    In production: uses PagerDuty REST API v2 to add a note.
    """
    if not PAGERDUTY_API_KEY:
        return False
    
    note_content = (
        f"🔍 SherLock Investigation Result\n"
        f"─────────────────────────\n"
        f"Investigation: {investigation.get('id')}\n"
        f"Confidence: {investigation.get('confidence', 0):.0%}\n"
        f"Root Cause: {investigation.get('rca_summary', 'Under investigation')}\n"
        f"Blast Radius: {', '.join(investigation.get('blast_radius', []))}\n"
        f"Recommended Action: {investigation.get('nba_action_id', 'None')}\n"
        f"─────────────────────────\n"
        f"View full investigation: https://dashboard.sherlock-sre.com/investigations/{investigation.get('id')}"
    )
    
    # In production:
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         f"https://api.pagerduty.com/incidents/{pagerduty_incident_id}/notes",
    #         headers={
    #             "Authorization": f"Token token={PAGERDUTY_API_KEY}",
    #             "Content-Type": "application/json"
    #         },
    #         json={"note": {"content": note_content}}
    #     )
    #     return response.status_code == 201
    
    return True
