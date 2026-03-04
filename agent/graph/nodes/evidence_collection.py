"""Step 4: Cypher query generation + execution."""

import os
import time
from typing import Optional

from agent.graph.state import InvestigationState
from agent.llm.client import chat_completion
from agent.prompts.cypher_synthesis import SYSTEM_PROMPT, build_user_prompt
from agent.tools.neo4j_tool import Neo4jTool

neo4j = Neo4jTool()
MAX_QUERIES_PER_HYPOTHESIS = int(os.environ.get("AGENT_MAX_EVIDENCE_QUERIES_PER_HYPOTHESIS", "3"))


async def _generate_cypher(question: str, context: dict) -> Optional[str]:
    """Generate Cypher from natural language question via LLM."""
    try:
        user_prompt = build_user_prompt(question, context)
        content = await chat_completion(
            model=os.environ.get("OPENAI_REASONING_MODEL", "gpt-4o"),
            temperature=0.0,
            max_tokens=500,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        cypher = (content or "").strip()
        if cypher and "CANNOT_GENERATE" not in cypher and "MATCH" in cypher.upper():
            return cypher
    except Exception:
        pass
    return None


async def collect_evidence(state: InvestigationState) -> dict:
    start = time.time()
    hypotheses = state.get("hypotheses", [])
    evidence_by_hypothesis = {}
    alert = state["alert"]
    context = {
        "service_name": alert.service_name,
        "alert_description": alert.description,
    }

    for h in hypotheses[:5]:  # Per spec AGENT_MAX_HYPOTHESES
        queries_nl = (h.confirming_evidence_queries or []) + (h.denying_evidence_queries or [])
        results = []
        for q in queries_nl[:MAX_QUERIES_PER_HYPOTHESIS]:
            cypher = None
            if "MATCH" in q.upper() and "MERGE" not in q.upper() and "CREATE" not in q.upper():
                cypher = q
            else:
                cypher = await _generate_cypher(q, context)
            if cypher:
                try:
                    r = await neo4j.query(cypher, {"service_name": alert.service_name})
                    results.extend(r)
                except Exception:
                    pass
        evidence_by_hypothesis[h.id] = results

    return {
        "evidence_by_hypothesis": evidence_by_hypothesis,
        "step_timings": {
            **state.get("step_timings", {}),
            "collect_evidence": time.time() - start,
        },
    }
