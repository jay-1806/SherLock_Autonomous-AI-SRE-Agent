-- graph/schema/indexes.cypher

CREATE INDEX service_team_idx IF NOT EXISTS FOR (s:Service) ON (s.team);
CREATE INDEX service_sla_idx IF NOT EXISTS FOR (s:Service) ON (s.sla_tier);
CREATE INDEX incident_severity_idx IF NOT EXISTS FOR (i:Incident) ON (i.severity);
CREATE INDEX incident_status_idx IF NOT EXISTS FOR (i:Incident) ON (i.status);
CREATE INDEX incident_start_time_idx IF NOT EXISTS FOR (i:Incident) ON (i.start_time);
CREATE INDEX deployment_timestamp_idx IF NOT EXISTS FOR (d:Deployment) ON (d.timestamp);
CREATE INDEX host_region_idx IF NOT EXISTS FOR (h:Host) ON (h.region);
CREATE INDEX anomaly_score_idx IF NOT EXISTS FOR (a:AnomalySignal) ON (a.score);
