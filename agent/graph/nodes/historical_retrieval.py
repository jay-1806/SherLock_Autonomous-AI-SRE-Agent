"""Step 2: Vector search for similar incidents."""

import time
from agent.graph.state import InvestigationState

# Placeholder — real implementation uses Neo4j vector index
# CALL db.index.vector.queryNodes('incident_embedding_idx', $top_k, $query_embedding)
# For local dev without embeddings, return empty list


async def retrieve_historical(state: InvestigationState) -> dict:
    start = time.time()
    # Placeholder: no vector index in local Neo4j community
    similar_incidents = []
    return {
        "similar_incidents": similar_incidents,
        "step_timings": {**state.get("step_timings", {}), "retrieve_historical": time.time() - start},
    }
