"""Load test fixtures — services, relationships, deployments for local dev and eval."""

import asyncio
import os
from datetime import datetime, timedelta
from neo4j import AsyncGraphDatabase


async def main():
    uri = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    user = os.environ.get("NEO4J_USERNAME", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "sherlock-local")

    driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    # Generic services
    services = [f"service-{i}" for i in range(1, 21)]

    # Eval-specific services (from labeled_incidents.json)
    eval_services = [
        "checkout-api",
        "order-service",
        "inventory-api",
        "auth-service",
        "search-api",
        "notify-worker",
        "api-gateway",
        "payment-gateway",
        "recommendation-service",
        "user-profile-api",
        "analytics-pipeline",
        "catalog-api",
        "shipping-service",
        "session-manager",
        "billing-worker",
        "cdn-origin",
        "ml-inference",
        "audit-logger",
        "rate-limiter",
        "health-check",
    ]
    all_services = list(dict.fromkeys(services + eval_services))

    async with driver.session() as session:
        for s in all_services:
            await session.run(
                "MERGE (s:Service {name: $name}) ON CREATE SET s.team = 'platform', s.sla_tier = 'tier-2'",
                {"name": s},
            )

        # Generic chain: service-1 -> service-2 -> ... -> service-20
        for i, s in enumerate(services[:-1]):
            await session.run(
                "MATCH (a:Service {name: $a}), (b:Service {name: $b}) MERGE (a)-[:CALLS]->(b)",
                {"a": s, "b": services[i + 1]},
            )

        # Eval topology: order-service -> payment-gateway, service-1 -> service-2
        await session.run(
            "MATCH (a:Service {name: $a}), (b:Service {name: $b}) MERGE (a)-[:CALLS]->(b)",
            {"a": "order-service", "b": "payment-gateway"},
        )
        await session.run(
            "MATCH (a:Service {name: $a}), (b:Service {name: $b}) MERGE (a)-[:CALLS]->(b)",
            {"a": "service-1", "b": "service-2"},
        )

        # Deployments for deploy-induced eval incidents (commit_sha, timestamp ~1 hour ago)
        now = datetime.utcnow()
        hour_ago = (now - timedelta(minutes=90)).strftime("%Y-%m-%dT%H:%M:%S")

        deployments = [
            ("checkout-api", "a3f2bc9", "deploy-001"),
            ("inventory-api", "b2e8c1a", "deploy-002"),
            ("api-gateway", "d4f1e2b", "deploy-003"),
            ("recommendation-service", "e5a9c3f", "deploy-004"),
            ("catalog-api", "f7b2d1e", "deploy-005"),
            ("rate-limiter", "g8c4h2a", "deploy-006"),
        ]
        for service_name, commit_sha, deploy_id in deployments:
            await session.run(
                """
                MERGE (s:Service {name: $service_name})
                MERGE (d:Deployment {deployment_id: $deploy_id})
                ON CREATE SET
                  d.service_name = $service_name,
                  d.commit_sha = $commit_sha,
                  d.deployer = 'eval-fixture',
                  d.timestamp = datetime($ts),
                  d.strategy = 'rolling',
                  d.rollback_available = true
                MERGE (s)-[:DEPLOYED_AS]->(d)
                """,
                {"service_name": service_name, "commit_sha": commit_sha, "deploy_id": deploy_id, "ts": hour_ago},
            )

    print(f"Loaded {len(all_services)} services, relationships, and {len(deployments)} deployments")
    await driver.close()


if __name__ == "__main__":
    asyncio.run(main())
