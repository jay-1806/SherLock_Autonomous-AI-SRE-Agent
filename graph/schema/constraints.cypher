-- graph/schema/constraints.cypher
-- Run once on Neo4j Aura instance initialization

CREATE CONSTRAINT service_name_unique IF NOT EXISTS
  FOR (s:Service) REQUIRE s.name IS UNIQUE;

CREATE CONSTRAINT host_id_unique IF NOT EXISTS
  FOR (h:Host) REQUIRE h.instance_id IS UNIQUE;

CREATE CONSTRAINT deployment_id_unique IF NOT EXISTS
  FOR (d:Deployment) REQUIRE d.deployment_id IS UNIQUE;

CREATE CONSTRAINT incident_id_unique IF NOT EXISTS
  FOR (i:Incident) REQUIRE i.incident_id IS UNIQUE;

CREATE CONSTRAINT config_change_id_unique IF NOT EXISTS
  FOR (c:ConfigChange) REQUIRE c.change_id IS UNIQUE;

CREATE CONSTRAINT service_requires_name IF NOT EXISTS
  FOR (s:Service) REQUIRE s.name IS NOT NULL;

CREATE CONSTRAINT incident_requires_severity IF NOT EXISTS
  FOR (i:Incident) REQUIRE i.severity IS NOT NULL;
