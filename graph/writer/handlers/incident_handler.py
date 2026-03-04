"""Incident node handler."""

from datetime import datetime
from ..neo4j_client import Neo4jClient


class IncidentHandler:
    def __init__(self, neo4j: Neo4jClient):
        self.neo4j = neo4j

    async def handle(self, signal: dict) -> None:
        """Write Incident node from incident event."""
        event_data = signal.get("tags", {})
        incident_id = event_data.get("incident_id", signal.get("signal_id", "unknown"))
        severity = event_data.get("severity", "P3")
        ts_raw = signal.get("timestamp_utc")
        if isinstance(ts_raw, str):
            timestamp = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        elif hasattr(ts_raw, "isoformat"):
            timestamp = ts_raw
        else:
            timestamp = datetime.utcnow()
        affected = event_data.get("affected_services", [signal.get("service_name")])
        affected = [affected] if isinstance(affected, str) else (affected or [])

        query = """
        MERGE (i:Incident {incident_id: $incident_id})
        ON CREATE SET
          i.alert_id = $alert_id,
          i.severity = $severity,
          i.start_time = datetime($ts),
          i.status = coalesce($status, 'active'),
          i.affected_services = $affected
        ON MATCH SET
          i.status = coalesce($status, i.status),
          i.affected_services = coalesce($affected, i.affected_services)
        """
        await self.neo4j.execute_write(
            query,
            {
                "incident_id": incident_id,
                "alert_id": event_data.get("alert_id"),
                "severity": severity,
                "ts": timestamp.isoformat(),
                "status": event_data.get("status", "active"),
                "affected": affected,
            },
        )
