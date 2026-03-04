"""Unit tests for graph writer handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from graph.writer.handlers.service_handler import ServiceHandler
from graph.writer.handlers.host_handler import HostHandler


@pytest.mark.asyncio
async def test_service_handler_upsert():
    neo4j = MagicMock()
    neo4j.execute_write = AsyncMock(return_value=[])
    handler = ServiceHandler(neo4j)

    await handler.upsert({
        "service_name": "checkout-api",
        "tags": {"team": "commerce", "sla_tier": "tier-1"},
    })

    neo4j.execute_write.assert_called_once()
    call_args = neo4j.execute_write.call_args
    assert "checkout-api" in str(call_args)
    assert "commerce" in str(call_args) or "tier-1" in str(call_args)


@pytest.mark.asyncio
async def test_host_handler_skips_without_host_id():
    neo4j = MagicMock()
    neo4j.execute_write = AsyncMock(return_value=[])
    handler = HostHandler(neo4j)

    await handler.upsert({"service_name": "api"})
    neo4j.execute_write.assert_not_called()


@pytest.mark.asyncio
async def test_host_handler_upsert():
    neo4j = MagicMock()
    neo4j.execute_write = AsyncMock(return_value=[])
    handler = HostHandler(neo4j)

    await handler.upsert({
        "service_name": "api",
        "host_id": "i-abc123",
        "tags": {"region": "us-east-1", "az": "us-east-1a"},
    })

    neo4j.execute_write.assert_called_once()
    call_args = neo4j.execute_write.call_args[0][1]
    assert call_args["instance_id"] == "i-abc123"
    assert call_args["service_name"] == "api"
