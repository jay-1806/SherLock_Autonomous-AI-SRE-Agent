"""Neo4j driver wrapper with retry logic."""

from typing import Optional
from neo4j import AsyncGraphDatabase, AsyncDriver
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


class Neo4jClient:
    def __init__(self, uri: str, username: str, password: str):
        self._driver: AsyncDriver = AsyncGraphDatabase.driver(
            uri,
            auth=(username, password),
            max_connection_pool_size=50,
            connection_timeout=10,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def execute_write(self, query: str, parameters: Optional[dict] = None) -> list:
        """Execute a write query with automatic retry on transient failures."""
        async with self._driver.session() as session:
            result = await session.run(query, parameters or {})
            return [record.data() async for record in result]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )
    async def execute_read(self, query: str, parameters: Optional[dict] = None) -> list:
        """Execute a read query with automatic retry."""
        async with self._driver.session() as session:
            result = await session.run(query, parameters or {})
            return [record.data() async for record in result]

    async def close(self):
        await self._driver.close()
