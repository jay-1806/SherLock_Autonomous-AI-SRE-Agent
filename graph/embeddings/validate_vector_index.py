"""Validate vector index with a test embedding insert + query (Neo4j Aura Enterprise)."""

import asyncio
import os
from neo4j import AsyncGraphDatabase


async def main():
    uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    user = os.environ.get("NEO4J_USERNAME", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "sherlock-local")

    driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    # Dummy 1536-dim vector (OpenAI text-embedding-3-small)
    dummy_vec = [0.0] * 1536
    dummy_vec[0] = 1.0  # Non-zero for cosine similarity

    async with driver.session() as session:
        # Create test incident with embedding
        await session.run(
            """
            MERGE (i:Incident {incident_id: 'vector-test-001'})
            ON CREATE SET
              i.severity = 'P3',
              i.start_time = datetime(),
              i.status = 'resolved',
              i.embedding = $vec
            ON MATCH SET i.embedding = $vec
            """,
            {"vec": dummy_vec},
        )
        # Query vector index
        result = await session.run(
            """
            CALL db.index.vector.queryNodes('incident_embedding_idx', 5, $query_vec)
            YIELD node, score
            RETURN node.incident_id AS id, score
            LIMIT 5
            """,
            {"query_vec": dummy_vec},
        )
        rows = [r async for r in result]
        # Cleanup
        await session.run("MATCH (i:Incident {incident_id: 'vector-test-001'}) DETACH DELETE i")

    print(f"Vector index OK: queried {len(rows)} results")
    await driver.close()


if __name__ == "__main__":
    asyncio.run(main())
