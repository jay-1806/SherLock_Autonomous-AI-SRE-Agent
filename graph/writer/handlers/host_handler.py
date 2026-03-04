"""Host node + RUNS_ON edge handler."""

from typing import Optional
from ..neo4j_client import Neo4jClient


class HostHandler:
    def __init__(self, neo4j: Neo4jClient):
        self.neo4j = neo4j

    async def upsert(self, signal: dict) -> None:
        """Upsert Host node and Service-RUNS_ON->Host edge from telemetry signal."""
        host_id = signal.get("host_id") or signal.get("tags", {}).get("host_id")
        service_name = signal.get("service_name")
        if not host_id or not service_name:
            return

        tags = signal.get("tags", {}) or {}
        region = tags.get("region", tags.get("aws_region", "unknown"))
        az = tags.get("az", tags.get("availability_zone", "unknown"))

        query = """
        MERGE (h:Host {instance_id: $instance_id})
        ON CREATE SET
          h.region = $region,
          h.az = $az,
          h.hostname = $hostname
        ON MATCH SET
          h.region = coalesce($region, h.region),
          h.az = coalesce($az, h.az)
        WITH h
        MATCH (s:Service {name: $service_name})
        MERGE (s)-[:RUNS_ON]->(h)
        """
        await self.neo4j.execute_write(
            query,
            {
                "instance_id": host_id,
                "region": region,
                "az": az,
                "hostname": tags.get("hostname"),
                "service_name": service_name,
            },
        )
