"""Apply Neo4j vector index (Neo4j Aura Enterprise only)."""

import asyncio
import os
from pathlib import Path
from neo4j import AsyncGraphDatabase


async def main():
    if not os.environ.get("NEO4J_ENTERPRISE"):
        print("Skipping vector index (set NEO4J_ENTERPRISE=1 for Aura Enterprise)")
        return

    uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    user = os.environ.get("NEO4J_USERNAME", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "sherlock-local")

    driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
    path = Path(__file__).parent / "indexes_vector.cypher"
    cypher = path.read_text()

    async with driver.session() as session:
        for stmt in cypher.split(";"):
            stmt = stmt.strip()
            if stmt and not stmt.startswith("--"):
                try:
                    await session.run(stmt)
                    print("Applied vector index")
                except Exception as e:
                    print(f"Vector index error: {e}")

    await driver.close()


if __name__ == "__main__":
    asyncio.run(main())
