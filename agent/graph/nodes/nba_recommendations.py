"""Step 8: Next-best-action recommendations."""

import time
from agent.graph.state import InvestigationState
from agent.models.investigation import Recommendation


async def generate_recommendations(state: InvestigationState) -> dict:
    start = time.time()
    root_cause = state.get("root_cause")
    hypotheses = state.get("hypotheses", [])
    deployment_history = state.get("deployment_history", [])

    recs = []
    if root_cause and deployment_history:
        d = deployment_history[0]
        sha = d.get("commit_sha", d.get("sha", "unknown"))[:8]
        recs.append(
            Recommendation(
                rank=1,
                action=f"Roll back to previous deployment (SHA: {sha})",
                rationale="Deploy-induced incidents typically resolve with rollback.",
                estimated_impact="high",
                estimated_risk="low",
                reversible=True,
                estimated_time_minutes=5,
            )
        )
    if not recs:
        recs.append(
            Recommendation(
                rank=1,
                action="Engage human SRE for manual investigation",
                rationale="Automated analysis insufficient. Manual triage required.",
                estimated_impact="medium",
                estimated_risk="low",
                reversible=True,
                estimated_time_minutes=15,
            )
        )

    return {
        "recommendations": recs,
        "step_timings": {
            **state.get("step_timings", {}),
            "generate_recommendations": time.time() - start,
        },
    }
