"""AnomalySignal node + OBSERVED_IN edge handler."""

import uuid
from datetime import datetime
from typing import Optional
from ..neo4j_client import Neo4jClient


class AnomalyHandler:
    def __init__(self, neo4j: Neo4jClient):
        self.neo4j = neo4j

    async def handle(self, signal: dict) -> None:
        """Write AnomalySignal node and OBSERVED_IN->Service edge."""
        service_name = signal.get("service_name")
        if not service_name:
            return

        tags = signal.get("tags", {}) or {}
        anomaly_id = tags.get("anomaly_id") or str(uuid.uuid4())[:12]
        score = float(tags.get("score", tags.get("anomaly_score", 0.8)))

        ts_raw = signal.get("timestamp_utc")
        if isinstance(ts_raw, str):
            timestamp = ts_raw
        elif hasattr(ts_raw, "isoformat"):
            timestamp = ts_raw.isoformat()
        else:
            timestamp = datetime.utcnow().isoformat()

        query = """
        MERGE (a:AnomalySignal {anomaly_id: $anomaly_id})
        ON CREATE SET
          a.score = $score,
          a.observed_at = datetime($ts)
        ON MATCH SET
          a.score = $score,
          a.observed_at = datetime($ts)
        WITH a
        MATCH (s:Service {name: $service_name})
        MERGE (a)-[:OBSERVED_IN]->(s)
        """
        await self.neo4j.execute_write(
            query,
            {
                "anomaly_id": anomaly_id,
                "score": score,
                "ts": timestamp,
                "service_name": service_name,
            },
        )
