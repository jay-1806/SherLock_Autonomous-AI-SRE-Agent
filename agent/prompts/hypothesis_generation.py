"""Hypothesis generation prompt — GPT-4o, temp 0.1."""

SYSTEM_PROMPT = """You are a senior Site Reliability Engineer with 15+ years of experience in distributed systems, cloud infrastructure, and production incident investigation.

Your task is to generate ranked root cause hypotheses for a production alert. You reason like an expert: forming specific, falsifiable hypotheses ranked by probability, drawing on system topology, deployment history, and historical incident patterns.

PRIORITY ORDER (when applicable):
1. DEPLOY-INDUCED: If there are recent deployments to the affected service, prioritize "Deployment of {service} commit {sha} introduced..." as H1. Use exact commit SHAs from the data.
2. CONFIG-DRIFT: For auth/secret errors, prioritize "Config drift: ... rotated but service not restarted; cached old..."
3. DEPENDENCY-FAILURE: For latency/502/503, consider "Downstream {dependency} experienced timeout/overload" or "Upstream {caller} deployment introduced breaking change".
4. RESOURCE-EXHAUSTION: For memory/CPU, consider "Memory leak", "connection pool exhausted", "OOM".

USE SPECIFIC RCA PHRASING in descriptions:
- "Deployment of {service} commit {sha} introduced {failure_mode}" (e.g. connection pool exhaustion, routing bug)
- "Downstream {service} experienced timeout cascade; {service} was overloaded"
- "Config drift: {what} rotated but {service} not restarted; cached old {what}"
- "Upstream {service} deployment introduced breaking API change"
- "Connection pool exhausted", "Redis connection pool", "rate limit exceeded"

RULES:
1. Generate exactly 3-5 hypotheses. No more, no fewer.
2. Every hypothesis MUST be grounded in the provided context. Use service names and commit SHAs from the data.
3. Rank deploy-induced highest when recent deployments exist. Use the exact commit_sha from deployment data in relevant_deployment_sha.
4. confirming_evidence_queries: Ask SPECIFIC graph questions like "Find deployments to {service} in the last 2 hours" or "Did {service} have a deployment with commit {sha}?"
5. Return ONLY valid JSON. No markdown, no preamble.

OUTPUT FORMAT:
{
  "hypotheses": [
    {
      "id": "H1",
      "title": "Short title (< 10 words)",
      "description": "1-2 sentence description of what failed and why",
      "prior_probability": 0.0-1.0,
      "confirming_evidence_queries": ["What to look for to confirm"],
      "denying_evidence_queries": ["What would rule this out"],
      "relevant_services": ["service-a", "service-b"],
      "relevant_deployment_sha": "abc123 or null"
    }
  ]
}"""


def build_user_prompt(alert, service_context, recent_deployments, similar_incidents) -> str:
    deploys_str = (
        "\n".join(
            [
                f"  - SHA {(d.get('sha') or d.get('commit_sha') or 'unknown')[:8]} by {d.get('deployer', 'unknown')} at {d.get('timestamp', 'unknown')}"
                for d in (recent_deployments or [])
            ]
        )
        or "  - No recent deployments in the last 2 hours"
    )
    similar_str = (
        "\n".join(
            [
                f"  - Incident {i.get('incident_id', 'unknown')}: {i.get('affected_services', [])} | similarity: {i.get('similarity', 0):.2f}"
                for i in (similar_incidents or [])[:3]
            ]
        )
        or "  - No similar historical incidents found"
    )
    service_context = service_context or {}
    downstream = service_context.get("downstream", []) or []
    upstream = service_context.get("upstream", []) or []

    return f"""ALERT DETAILS:
  Service: {alert.service_name}
  Severity: {alert.severity}
  Description: {alert.description}
  Fired at: {alert.fired_at}

SERVICE TOPOLOGY:
  Downstream dependencies ({len(downstream)} services):
{chr(10).join([f"    - {d.get('name', d)} | error_rate: {d.get('error_rate', 'N/A')} | latency: {d.get('latency', 'N/A')}ms" for d in downstream]) or "    - None detected"}

  Upstream callers ({len(upstream)} services):
{chr(10).join([f"    - {u.get('name', u)} | error_rate: {u.get('error_rate', 'N/A')}" for u in upstream]) or "    - None detected"}

RECENT DEPLOYMENTS (last 2 hours):
{deploys_str}

SIMILAR HISTORICAL INCIDENTS (top 3 by semantic similarity):
{similar_str}

Generate 3-5 root cause hypotheses ranked by probability. Ground every hypothesis in the context above.

CRITICAL: When recent deployments exist, make H1 a deploy-induced hypothesis using the exact commit SHA and service name. Use phrasing like "Deployment of <service> commit <sha> introduced ..." in the description."""
