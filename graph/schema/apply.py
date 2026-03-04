"""Apply Neo4j constraints and indexes."""

import asyncio
import os
from pathlib import Path
from neo4j import AsyncGraphDatabase


async def main():
    uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    user = os.environ.get("NEO4J_USERNAME", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "sherlock-local")

    driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    base = Path(__file__).parent
    for fname in ["constraints.cypher", "indexes.cypher"]:
        path = base / fname
        if path.exists():
            cypher = path.read_text()
            async with driver.session() as session:
                for stmt in cypher.split(";"):
                    stmt = stmt.strip()
                    if stmt:
                        try:
                            await session.run(stmt)
                            print(f"Applied: {stmt[:60]}...")
                        except Exception as e:
                            if "already exists" in str(e).lower():
                                print(f"Skip (exists): {stmt[:50]}...")
                            else:
                                print(f"Error: {e}")

    await driver.close()


if __name__ == "__main__":
    asyncio.run(main())
