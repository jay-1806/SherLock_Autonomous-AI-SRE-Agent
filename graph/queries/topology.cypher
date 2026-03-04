-- Get immediate dependencies of a service (upstream + downstream)
MATCH (s:Service {name: $service_name})
OPTIONAL MATCH (s)-[calls_out:CALLS]->(downstream:Service)
OPTIONAL MATCH (upstream:Service)-[calls_in:CALLS]->(s)
RETURN s,
       collect(DISTINCT {service: downstream, relationship: calls_out}) AS downstream_deps,
       collect(DISTINCT {service: upstream, relationship: calls_in}) AS upstream_deps
