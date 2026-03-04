"""Neo4j LangChain tool wrapper."""

import os
from typing import Optional
from neo4j import AsyncGraphDatabase
from tenacity import retry, stop_after_attempt, wait_exponential


class Neo4jTool:
    def __init__(self):
        self._driver = None

    def _get_driver(self):
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                os.environ["NEO4J_URI"],
                auth=(
                    os.environ.get("NEO4J_USERNAME", "neo4j"),
                    os.environ["NEO4J_PASSWORD"],
                ),
            )
        return self._driver

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5), reraise=True)
    async def query(self, cypher: str, params: Optional[dict] = None) -> list:
        """Execute read-only Cypher query."""
        driver = self._get_driver()
        async with driver.session() as session:
            result = await session.run(cypher, params or {})
            return [record.data() async for record in result]
