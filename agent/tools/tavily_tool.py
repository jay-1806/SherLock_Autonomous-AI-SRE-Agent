"""Tavily search tool — max 3 calls per investigation."""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

MAX_CALLS = int(os.environ.get("TAVILY_MAX_CALLS_PER_INVESTIGATION", "3"))


class TavilyInvestigationTool:
    def __init__(self):
        self._call_count = 0
        self._client = None

    def _get_client(self):
        if self._client is None:
            api_key = os.environ.get("TAVILY_API_KEY", "").strip()
            if not api_key or api_key in ("...", "tvly-..."):
                logger.info("TAVILY_API_KEY not set; Tavily search disabled")
                return None
            try:
                from tavily import TavilyClient

                self._client = TavilyClient(api_key=api_key)
            except ImportError:
                logger.warning("tavily-python not installed; Tavily search disabled")
                return None
        return self._client

    async def search(self, query: str, search_type: str = "general") -> list[dict]:
        if self._call_count >= MAX_CALLS:
            logger.warning("Tavily call budget exhausted. Skipping: %s", query[:50])
            return []

        client = self._get_client()
        if not client:
            return []

        self._call_count += 1
        logger.info("Tavily search [%s/%s]: %s", self._call_count, MAX_CALLS, query[:80])

        try:
            result = client.search(
                query=query,
                search_depth=os.environ.get("TAVILY_SEARCH_DEPTH", "advanced"),
                max_results=int(os.environ.get("TAVILY_MAX_RESULTS", "5")),
            )
            return result.get("results", [])
        except Exception as e:
            logger.error("Tavily search failed: %s", e)
            return []
