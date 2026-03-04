"""Step 1: Fetch alert context from Neo4j."""

import time
from agent.graph.state import InvestigationState
from agent.tools.neo4j_tool import Neo4jTool

neo4j = Neo4jTool()

CONTEXT_QUERY = """
MATCH (s:Service {name: $service_name})
OPTIONAL MATCH (s)-[calls:CALLS]->(downstream:Service)
OPTIONAL MATCH (upstream:Service)-[called_by:CALLS]->(s)
OPTIONAL MATCH (s)-[:RUNS_ON]->(host:Host)
OPTIONAL MATCH (s)-[:DEPLOYED_AS]->(recent_deploy:Deployment)
  WHERE recent_deploy.timestamp >= datetime() - duration({hours: 4})
RETURN s AS service,
       collect(DISTINCT {name: downstream.name, error_rate: calls.error_rate, latency: calls.avg_latency_ms}) AS downstream,
       collect(DISTINCT {name: upstream.name, error_rate: called_by.error_rate}) AS upstream,
       collect(DISTINCT {instance_id: host.instance_id, az: host.az, cpu: host.cpu_util, mem: host.mem_util}) AS hosts,
       collect(DISTINCT {sha: recent_deploy.commit_sha, deployer: recent_deploy.deployer, timestamp: toString(recent_deploy.timestamp)}) AS recent_deploys
"""

DEPLOY_QUERY = """
MATCH (s:Service {name: $service_name})-[:DEPLOYED_AS]->(d:Deployment)
WHERE d.timestamp >= datetime() - duration({minutes: $window_minutes})
RETURN d ORDER BY d.timestamp DESC LIMIT 5
"""


async def fetch_context(state: InvestigationState) -> dict:
    start = time.time()
    service_name = state["alert"].service_name

    try:
        context_results = await neo4j.query(CONTEXT_QUERY, {"service_name": service_name})
        deploy_results = await neo4j.query(
            DEPLOY_QUERY, {"service_name": service_name, "window_minutes": 120}
        )
    except Exception:
        context_results = []
        deploy_results = []

    ctx = context_results[0] if context_results else {}
    deploys = [r["d"] for r in deploy_results] if deploy_results else []

    return {
        "affected_service_context": ctx,
        "deployment_history": deploys,
        "step_timings": {**state.get("step_timings", {}), "fetch_context": time.time() - start},
    }
