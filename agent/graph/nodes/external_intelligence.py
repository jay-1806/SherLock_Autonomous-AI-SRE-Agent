"""Step 5: Tavily search for CVE, vendor status, runbooks."""

import time
from agent.graph.state import InvestigationState
from agent.tools.tavily_tool import TavilyInvestigationTool

tavily = TavilyInvestigationTool()


async def fetch_external_intelligence(state: InvestigationState) -> dict:
    start = time.time()
    alert = state["alert"]
    query = f"{alert.service_name} {alert.description} incident root cause"
    results = await tavily.search(query, search_type="general")

    return {
        "external_sources": results,
        "step_timings": {
            **state.get("step_timings", {}),
            "fetch_external_intelligence": time.time() - start,
        },
    }
