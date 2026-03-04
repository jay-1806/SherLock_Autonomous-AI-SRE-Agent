"""Step 6: GPT-4o evidence weighing — rank conclusions."""

import time
from agent.graph.state import InvestigationState


def _evidence_has_deployment(ev: list, commit_sha: str) -> bool:
    """Check if evidence contains a deployment with matching commit_sha."""
    if not commit_sha or not ev:
        return False
    sha_lower = str(commit_sha).lower()[:8]
    for r in ev:
        if isinstance(r, dict):
            c = r.get("commit_sha") or r.get("sha") or r.get("d", {}).get("commit_sha") if isinstance(r.get("d"), dict) else None
            if c and str(c).lower()[:8] == sha_lower:
                return True
        elif hasattr(r, "get"):
            c = r.get("commit_sha") or r.get("sha")
            if c and str(c).lower()[:8] == sha_lower:
                return True
    return False


async def synthesize_evidence(state: InvestigationState) -> dict:
    start = time.time()
    hypotheses = state.get("hypotheses", [])
    evidence = state.get("evidence_by_hypothesis", {})
    deployment_history = state.get("deployment_history", [])

    ranked = []
    for h in hypotheses:
        ev = evidence.get(h.id, [])
        base = h.prior_probability * (1.0 + 0.1 * len(ev))
        # Strong boost when deployment evidence matches hypothesis (deploy-induced)
        if h.relevant_deployment_sha and _evidence_has_deployment(ev, h.relevant_deployment_sha):
            base = max(base, 0.85)
        # Moderate boost when deployment history exists and hypothesis mentions deployment
        if deployment_history and "deployment" in h.description.lower() and "commit" in h.description.lower():
            base = max(base, h.prior_probability + 0.2)
        ranked.append({"hypothesis_id": h.id, "posterior": min(base, 0.99), "evidence_count": len(ev)})

    ranked.sort(key=lambda x: x["posterior"], reverse=True)

    root_cause = None
    root_thresh = float(__import__("os").environ.get("ROOT_CAUSE_POSTERIOR_THRESHOLD", "0.35"))
    if ranked:
        top = ranked[0]
        top_h = next((h for h in hypotheses if h.id == top["hypothesis_id"]), None)
        if top_h and top["posterior"] > root_thresh:
            root_cause = {
                "description": top_h.description,
                "posterior": top["posterior"],
            }

    return {
        "ranked_conclusions": ranked,
        "root_cause": root_cause,
        "confidence_score": top["posterior"] if ranked else 0.0,
        "step_timings": {
            **state.get("step_timings", {}),
            "synthesize_evidence": time.time() - start,
        },
    }
