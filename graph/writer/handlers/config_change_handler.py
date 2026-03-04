"""ConfigChange node handler."""

import uuid
from datetime import datetime
from ..neo4j_client import Neo4jClient


class ConfigChangeHandler:
    def __init__(self, neo4j: Neo4jClient):
        self.neo4j = neo4j

    async def handle(self, signal: dict) -> None:
        """Write ConfigChange node from config mutation event."""
        tags = signal.get("tags", {}) or {}
        change_id = tags.get("change_id") or str(uuid.uuid4())[:12]
        service_name = signal.get("service_name", tags.get("service"))

        ts_raw = signal.get("timestamp_utc")
        if isinstance(ts_raw, str):
            timestamp = ts_raw
        elif hasattr(ts_raw, "isoformat"):
            timestamp = ts_raw.isoformat()
        else:
            timestamp = datetime.utcnow().isoformat()

        change_type = tags.get("change_type", tags.get("config_change_type", "unknown"))

        query = """
        MERGE (c:ConfigChange {change_id: $change_id})
        ON CREATE SET
          c.service_name = $service_name,
          c.change_type = $change_type,
          c.timestamp = datetime($ts)
        ON MATCH SET
          c.timestamp = datetime($ts)
        """
        await self.neo4j.execute_write(
            query,
            {
                "change_id": change_id,
                "service_name": service_name or "unknown",
                "change_type": change_type,
                "ts": timestamp,
            },
        )
