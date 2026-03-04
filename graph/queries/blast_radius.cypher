-- Find all services that could be affected if $service_name fails
MATCH (failing:Service {name: $service_name})
MATCH (caller:Service)-[:CALLS*1..3]->(failing)
RETURN DISTINCT caller.name AS affected_service,
       caller.sla_tier AS sla_tier,
       caller.team AS team
ORDER BY
  CASE caller.sla_tier
    WHEN 'tier-0' THEN 0
    WHEN 'tier-1' THEN 1
    WHEN 'tier-2' THEN 2
    ELSE 3
  END
