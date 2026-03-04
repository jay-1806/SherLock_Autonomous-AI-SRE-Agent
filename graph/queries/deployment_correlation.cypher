-- Find deployments to $service_name in the last $minutes_window minutes
MATCH (s:Service {name: $service_name})-[:DEPLOYED_AS]->(d:Deployment)
WHERE d.timestamp >= datetime() - duration({minutes: $minutes_window})
RETURN d.deployment_id, d.commit_sha, d.deployer, d.timestamp, d.strategy
ORDER BY d.timestamp DESC
LIMIT 5
