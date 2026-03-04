"""Graph writer Kafka consumer entry point."""

import asyncio
import json
import logging
import os

from aiokafka import AIOKafkaConsumer

from ingestion.schemas.telemetry_signal import TelemetrySignal
from graph.writer.handlers.anomaly_handler import AnomalyHandler
from graph.writer.handlers.config_change_handler import ConfigChangeHandler
from graph.writer.handlers.deployment_handler import DeploymentHandler
from graph.writer.handlers.host_handler import HostHandler
from graph.writer.handlers.incident_handler import IncidentHandler
from graph.writer.handlers.service_handler import ServiceHandler
from graph.writer.neo4j_client import Neo4jClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOPICS = [
    os.environ.get("KAFKA_TOPIC_TELEMETRY_METRICS", "telemetry.metrics"),
    os.environ.get("KAFKA_TOPIC_TELEMETRY_LOGS", "telemetry.logs"),
    os.environ.get("KAFKA_TOPIC_TELEMETRY_TRACES", "telemetry.traces"),
    os.environ.get("KAFKA_TOPIC_TELEMETRY_EVENTS", "telemetry.events"),
]


async def main() -> None:
    neo4j = Neo4jClient(
        uri=os.environ["NEO4J_URI"],
        username=os.environ.get("NEO4J_USERNAME", "neo4j"),
        password=os.environ["NEO4J_PASSWORD"],
    )

    handlers = {
        "deployment": DeploymentHandler(neo4j),
        "service_health": ServiceHandler(neo4j),
        "incident": IncidentHandler(neo4j),
        "host": HostHandler(neo4j),
        "anomaly": AnomalyHandler(neo4j),
        "config_change": ConfigChangeHandler(neo4j),
    }

    consumer = AIOKafkaConsumer(
        *TOPICS,
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        group_id=os.environ.get("KAFKA_CONSUMER_GROUP_GRAPH_WRITER", "graph-writer-group"),
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=False,
    )

    await consumer.start()
    logger.info("Graph writer consumer started")

    try:
        async for msg in consumer:
            try:
                raw = msg.value
                if isinstance(raw.get("timestamp_utc"), str):
                    pass  # Pydantic will parse
                signal = TelemetrySignal(**raw)
                await route_signal(signal, handlers)
                await consumer.commit()
            except Exception as e:
                logger.error("Failed to process signal: %s", e, exc_info=True)
    finally:
        await consumer.stop()
        await neo4j.close()


async def route_signal(signal: TelemetrySignal, handlers: dict) -> None:
    """Route normalized signal to the appropriate graph handler."""
    sig_dict = signal.model_dump(mode="json")

    await handlers["service_health"].upsert(sig_dict)

    if signal.host_id:
        await handlers["host"].upsert(sig_dict)

    if signal.signal_type == "event":
        event_type = signal.tags.get("event.type", signal.tags.get("event_type"))
        if event_type == "deployment":
            await handlers["deployment"].handle(sig_dict)
        elif event_type == "incident":
            await handlers["incident"].handle(sig_dict)
        elif event_type == "config_change":
            await handlers["config_change"].handle(sig_dict)
        elif event_type == "anomaly":
            await handlers["anomaly"].handle(sig_dict)


if __name__ == "__main__":
    asyncio.run(main())
