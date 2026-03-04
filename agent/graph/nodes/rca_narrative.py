"""Step 7: Root cause narrative generation."""

import time
from agent.graph.state import InvestigationState


async def generate_rca_narrative(state: InvestigationState) -> dict:
    start = time.time()
    root_cause = state.get("root_cause")
    alert = state["alert"]

    if root_cause:
        narrative = f"## Root Cause Summary\n\n{root_cause.get('description', 'Unknown')}\n\n**Affected service:** {alert.service_name}\n**Confidence:** {root_cause.get('posterior', 0):.2f}"
    else:
        narrative = f"## Investigation Inconclusive\n\nInsufficient evidence to determine root cause for {alert.service_name}. Human review recommended."

    return {
        "narrative_summary": narrative,
        "step_timings": {
            **state.get("step_timings", {}),
            "generate_rca_narrative": time.time() - start,
        },
    }
