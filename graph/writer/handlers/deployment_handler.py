"""Deployment node + DEPLOYED_AS edge handler."""

import uuid
from datetime import datetime
from ..neo4j_client import Neo4jClient


class DeploymentHandler:
    def __init__(self, neo4j: Neo4jClient):
        self.neo4j = neo4j

    async def handle(self, signal: dict) -> None:
        """Write Deployment node and DEPLOYED_AS edge from deployment event."""
        event_data = signal.get("tags", {})
        service_name = signal.get("service_name", event_data.get("service"))
        if not service_name:
            return

        deployment_id = event_data.get("deployment_id") or str(uuid.uuid4())[:12]
        commit_sha = event_data.get("commit_sha", event_data.get("sha", "unknown"))
        deployer = event_data.get("deployer", event_data.get("deployer_email"))
        ts_raw = signal.get("timestamp_utc")
        if isinstance(ts_raw, str):
            timestamp = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        elif hasattr(ts_raw, "isoformat"):
            timestamp = ts_raw
        else:
            timestamp = datetime.utcnow()

        query = """
        MERGE (s:Service {name: $service_name})
        MERGE (d:Deployment {deployment_id: $deployment_id})
        ON CREATE SET
          d.service_name = $service_name,
          d.commit_sha = $commit_sha,
          d.deployer = $deployer,
          d.timestamp = datetime($ts),
          d.strategy = coalesce($strategy, 'rolling'),
          d.rollback_available = true
        ON MATCH SET
          d.commit_sha = $commit_sha,
          d.deployer = $deployer,
          d.timestamp = datetime($ts)
        MERGE (s)-[:DEPLOYED_AS]->(d)
        """
        await self.neo4j.execute_write(
            query,
            {
                "service_name": service_name,
                "deployment_id": deployment_id,
                "commit_sha": commit_sha,
                "deployer": deployer,
                "ts": timestamp.isoformat(),
                "strategy": event_data.get("strategy"),
            },
        )
