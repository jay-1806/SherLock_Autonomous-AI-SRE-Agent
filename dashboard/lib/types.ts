/**
 * Type definitions for SherLock dashboard
 */

export type InvestigationStatus = 'open' | 'in_progress' | 'resolved' | 'closed';
export type InvestigationSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface TimelineEvent {
  timestamp: string;
  event: string;
  source: string;
}

export interface Hypothesis {
  hypothesis: string;
  confidence: number;
  status: string;
}

export interface Evidence {
  type: string;
  source: string;
  description: string;
}

export interface InvestigationSummary {
  id: string;
  title: string;
  status: InvestigationStatus;
  severity: InvestigationSeverity;
  service: string;
  created_at: string;
  confidence?: number;
  rca_summary?: string;
}

export interface Investigation extends InvestigationSummary {
  description: string;
  updated_at: string;
  assigned_to: string | null;
  timeline: TimelineEvent[] | null;
  hypotheses?: Hypothesis[];
  evidence?: Evidence[];
  blast_radius?: string[];
  root_cause: string | null;
  remediation: string | null;
  nba_action_id?: string | null;
}

// Services
export type ServiceStatus = 'healthy' | 'degraded' | 'critical' | 'unknown';

export interface ServiceSummary {
  name: string;
  display_name: string;
  status: ServiceStatus;
  health_score: number;
  team: string;
  sla_tier: string;
  last_deployment: string;
  active_incidents: number;
}

export interface ServiceDetail extends ServiceSummary {
  dependencies: string[];
  region: string;
  environment: string;
  incident_history: {
    id: string;
    title: string;
    date: string;
    severity: string;
    root_cause: string;
  }[];
}

// Remediation
export type RiskLevel = 'low' | 'medium' | 'high';

export interface RemediationAction {
  action_id: string;
  name: string;
  description: string;
  trigger_condition: string;
  risk_level: RiskLevel;
  requires_mfa: boolean;
  category: string;
  estimated_duration: string;
  rollback_procedure: string;
  last_executed: string | null;
  execution_count: number;
  success_rate: number | null;
}

export interface ExecutionLogEntry {
  execution_id: string;
  action_id: string;
  action_name: string;
  investigation_id: string;
  triggered_by: string;
  status: string;
  executed_at: string;
  duration_seconds: number;
  pre_state: Record<string, any>;
  post_state: Record<string, any>;
  dry_run: boolean;
}

// KPIs
export interface KPI {
  name: string;
  value: string;
  target: string;
  trend: string;
  change: string;
  status: string;
  history: number[];
}

export interface EvalSummary {
  last_updated: string;
  period: string;
  kpis: KPI[];
  summary_stats: {
    total_investigations_30d: number;
    auto_triggered: number;
    manual_triggered: number;
    avg_confidence: number;
    total_remediations: number;
    successful_remediations: number;
    top_recurring_causes: { cause: string; count: number }[];
  };
}

// Feedback
export interface FeedbackEntry {
  investigation_id: string;
  rating: 'correct' | 'partially_correct' | 'incorrect';
  comment: string;
  submitted_by: string;
  submitted_at: string;
}

// Graph
export interface GraphNode {
  id: string;
  label: string;
  type: 'service' | 'host' | 'deployment' | 'incident';
  status: string;
  health: number | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  call_volume: number | null;
  error_rate: number | null;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
