-- Vector index for incident semantic search (Neo4j Aura Enterprise only)
-- Run separately: NEO4J_ENTERPRISE=1 uv run python -m graph.schema.apply_vector
CREATE VECTOR INDEX incident_embedding_idx IF NOT EXISTS
  FOR (i:Incident) ON (i.embedding)
  OPTIONS {
    indexConfig: {
      `vector.dimensions`: 1536,
      `vector.similarity_function`: 'cosine'
    }
  };
