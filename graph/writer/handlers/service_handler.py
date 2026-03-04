"""Service node upsert handler."""

from ..neo4j_client import Neo4jClient


class ServiceHandler:
    def __init__(self, neo4j: Neo4jClient):
        self.neo4j = neo4j

    async def upsert(self, signal: dict) -> None:
        """Upsert Service node from telemetry signal."""
        service_name = signal.get("service_name", "unknown")
        if not service_name:
            return

        query = """
        MERGE (s:Service {name: $name})
        ON CREATE SET s.team = $team, s.sla_tier = $sla_tier, s.last_updated_utc = datetime()
        ON MATCH SET s.last_updated_utc = datetime()
        """
        await self.neo4j.execute_write(
            query,
            {
                "name": service_name,
                "team": signal.get("tags", {}).get("team"),
                "sla_tier": signal.get("tags", {}).get("sla_tier", "tier-2"),
            },
        )
