/**
 * Offline demo data — dashboard works without backend API
 */
import type {
  EvalSummary,
  ExecutionLogEntry,
  FeedbackEntry,
  Investigation,
  InvestigationSummary,
  RemediationAction,
  ServiceSummary,
} from './types';

export const DEMO_INVESTIGATIONS: Investigation[] = [
  {
    id: 'inv-001',
    title: 'API Gateway High Latency',
    description:
      'Increased response times on API Gateway. P99 latency exceeded 2s. Correlated with marketing campaign traffic spike.',
    status: 'in_progress',
    severity: 'high',
    service: 'api-gateway',
    created_at: '2026-02-27T10:30:00Z',
    updated_at: '2026-02-27T11:45:00Z',
    assigned_to: 'oncall-team',
    confidence: 0.87,
    rca_summary: 'Database connection pool exhaustion from sudden traffic spike.',
    hypotheses: [
      { hypothesis: 'Database connection pool exhaustion', confidence: 0.87, status: 'confirmed' },
      { hypothesis: 'CDN cache miss rate increase', confidence: 0.32, status: 'rejected' },
    ],
    evidence: [
      { type: 'metric', source: 'CloudWatch', description: 'DB connection count at 100% capacity since 10:28 UTC' },
      { type: 'log', source: 'ECS', description: 'Connection timeout errors in api-gateway task logs' },
    ],
    blast_radius: ['api-gateway', 'user-service', 'order-service'],
    timeline: [
      { timestamp: '2026-02-27T10:30:00Z', event: 'Alert: High latency (P99 > 2s)', source: 'datadog' },
      { timestamp: '2026-02-27T10:32:00Z', event: 'Investigation created automatically', source: 'sherlock' },
      { timestamp: '2026-02-27T11:00:00Z', event: 'Root cause confirmed: DB pool exhaustion', source: 'sherlock' },
      { timestamp: '2026-02-27T11:15:00Z', event: 'NBA recommended: ECS Scale-Out (ACT-002)', source: 'sherlock' },
    ],
    root_cause: 'Database connection pool exhausted due to 340% traffic spike',
    remediation: 'Scale up DB connections. Recommended: ACT-002 (ECS Scale-Out)',
    nba_action_id: 'ACT-002',
  },
  {
    id: 'inv-002',
    title: 'Payment Service 5xx Errors',
    description: 'Spike in 500 errors from payment service. Error rate exceeded 5%. Customer-facing impact.',
    status: 'open',
    severity: 'critical',
    service: 'payment-service',
    created_at: '2026-02-27T14:00:00Z',
    updated_at: '2026-02-27T14:15:00Z',
    assigned_to: null,
    confidence: 0.72,
    rca_summary: 'Investigation in progress — deployment correlation detected.',
    hypotheses: [
      { hypothesis: 'Bad deployment v2.14.3 rolled out 25 min ago', confidence: 0.72, status: 'investigating' },
      { hypothesis: 'Downstream payment provider outage', confidence: 0.45, status: 'investigating' },
    ],
    evidence: [
      { type: 'deployment', source: 'GitHub', description: 'payment-service v2.14.3 deployed 25 min before alert' },
      { type: 'metric', source: 'Prometheus', description: 'Error rate jumped from 0.2% to 7.8%' },
    ],
    blast_radius: ['payment-service', 'checkout-service', 'order-service'],
    timeline: [
      { timestamp: '2026-02-27T14:00:00Z', event: 'Alert: 5xx error rate > 5%', source: 'pagerduty' },
      { timestamp: '2026-02-27T14:02:00Z', event: 'Investigation created automatically', source: 'sherlock' },
      { timestamp: '2026-02-27T14:05:00Z', event: 'Deployment correlation: v2.14.3', source: 'sherlock' },
    ],
    root_cause: null,
    remediation: null,
    nba_action_id: null,
  },
  {
    id: 'inv-003',
    title: 'Cache Service Memory Pressure',
    description: 'Redis high memory usage. Eviction rate increasing.',
    status: 'resolved',
    severity: 'medium',
    service: 'cache-service',
    created_at: '2026-02-26T08:00:00Z',
    updated_at: '2026-02-26T12:30:00Z',
    assigned_to: 'platform-team',
    confidence: 0.94,
    rca_summary: 'Missing TTL on session cache entries caused unbounded growth.',
    hypotheses: [{ hypothesis: 'Missing TTL on cache entries', confidence: 0.94, status: 'confirmed' }],
    evidence: [
      { type: 'metric', source: 'Prometheus', description: 'Memory grew linearly over 72 hours' },
      { type: 'config', source: 'Redis', description: 'Session keys missing EXPIRE directive' },
    ],
    blast_radius: ['cache-service', 'user-service'],
    timeline: [
      { timestamp: '2026-02-26T08:00:00Z', event: 'Alert: Memory > 80%', source: 'prometheus' },
      { timestamp: '2026-02-26T12:30:00Z', event: 'Investigation resolved', source: 'sherlock' },
    ],
    root_cause: 'Missing TTL on session cache entries',
    remediation: 'Added 24h TTL. Flushed 2.1M stale keys.',
    nba_action_id: 'ACT-008',
  },
  {
    id: 'inv-005',
    title: 'Order Service CPU Saturation',
    description: 'ECS CPU above 90% for 8 minutes. Auto-scaling not triggering.',
    status: 'resolved',
    severity: 'high',
    service: 'order-service',
    created_at: '2026-02-27T06:15:00Z',
    updated_at: '2026-02-27T07:30:00Z',
    assigned_to: 'platform-team',
    confidence: 0.92,
    rca_summary: 'Auto-scaling threshold misconfigured at 95% instead of 70%.',
    hypotheses: [{ hypothesis: 'Auto-scaling policy misconfiguration', confidence: 0.92, status: 'confirmed' }],
    evidence: [
      { type: 'config', source: 'Terraform', description: 'Target tracking threshold at 95% (should be 70%)' },
    ],
    blast_radius: ['order-service', 'payment-service', 'notification-service'],
    timeline: [
      { timestamp: '2026-02-27T06:15:00Z', event: 'Alert: CPU > 90%', source: 'cloudwatch' },
      { timestamp: '2026-02-27T07:30:00Z', event: 'Investigation resolved', source: 'sherlock' },
    ],
    root_cause: 'Auto-scaling threshold misconfigured at 95% CPU',
    remediation: 'Fixed threshold to 70%. Scaled to 5 tasks.',
    nba_action_id: 'ACT-001',
  },
];

export function getDemoInvestigationSummaries(): InvestigationSummary[] {
  return DEMO_INVESTIGATIONS.map((inv) => ({
    id: inv.id,
    title: inv.title,
    status: inv.status,
    severity: inv.severity,
    service: inv.service,
    created_at: inv.created_at,
    confidence: inv.confidence,
    rca_summary: inv.rca_summary,
  }));
}

export function getDemoInvestigationById(id: string): Investigation | undefined {
  return DEMO_INVESTIGATIONS.find((inv) => inv.id === id);
}

export const DEMO_SERVICES: ServiceSummary[] = [
  { name: 'api-gateway', display_name: 'API Gateway', status: 'degraded', health_score: 72, team: 'platform-team', sla_tier: 'P1', last_deployment: '2026-02-27T08:00:00Z', active_incidents: 1 },
  { name: 'payment-service', display_name: 'Payment Service', status: 'critical', health_score: 35, team: 'payments-team', sla_tier: 'P1', last_deployment: '2026-02-27T13:35:00Z', active_incidents: 1 },
  { name: 'cache-service', display_name: 'Cache Service (Redis)', status: 'healthy', health_score: 98, team: 'platform-team', sla_tier: 'P2', last_deployment: '2026-02-26T12:30:00Z', active_incidents: 0 },
  { name: 'auth-service', display_name: 'Auth Service', status: 'healthy', health_score: 99, team: 'security-team', sla_tier: 'P1', last_deployment: '2026-02-24T14:00:00Z', active_incidents: 0 },
  { name: 'order-service', display_name: 'Order Service', status: 'healthy', health_score: 95, team: 'commerce-team', sla_tier: 'P1', last_deployment: '2026-02-27T06:00:00Z', active_incidents: 0 },
  { name: 'user-service', display_name: 'User Service', status: 'healthy', health_score: 97, team: 'identity-team', sla_tier: 'P2', last_deployment: '2026-02-26T10:00:00Z', active_incidents: 0 },
  { name: 'notification-service', display_name: 'Notification Service', status: 'healthy', health_score: 100, team: 'platform-team', sla_tier: 'P3', last_deployment: '2026-02-25T09:00:00Z', active_incidents: 0 },
  { name: 'image-processor', display_name: 'Image Processor (Lambda)', status: 'healthy', health_score: 96, team: 'media-team', sla_tier: 'P3', last_deployment: '2026-02-26T17:00:00Z', active_incidents: 0 },
];

export const DEMO_REMEDIATION_CATALOG: RemediationAction[] = [
  { action_id: 'ACT-001', name: 'ECS Service Restart', description: 'Restart ECS tasks to recover from hung processes.', trigger_condition: 'CPU > 90% for 5 min', risk_level: 'low', requires_mfa: false, category: 'compute', estimated_duration: '2-3 min', rollback_procedure: 'Auto-restore previous revision', last_executed: '2026-02-27T07:30:00Z', execution_count: 12, success_rate: 0.92 },
  { action_id: 'ACT-002', name: 'ECS Desired Count Scale-Out', description: 'Increase task count for traffic spikes.', trigger_condition: 'Error rate > 5% with CPU > 70%', risk_level: 'low', requires_mfa: false, category: 'compute', estimated_duration: '3-5 min', rollback_procedure: 'Reduce desired count', last_executed: '2026-02-27T11:15:00Z', execution_count: 8, success_rate: 1.0 },
  { action_id: 'ACT-003', name: 'Lambda Concurrency Increase', description: 'Raise reserved concurrency for throttled functions.', trigger_condition: 'Throttle rate > 10%', risk_level: 'low', requires_mfa: false, category: 'serverless', estimated_duration: '< 1 min', rollback_procedure: 'Reduce concurrency', last_executed: '2026-02-26T19:30:00Z', execution_count: 5, success_rate: 1.0 },
  { action_id: 'ACT-005', name: 'Deployment Rollback', description: 'Roll back to last known good revision.', trigger_condition: 'Error spike post-deploy', risk_level: 'medium', requires_mfa: true, category: 'deployment', estimated_duration: '3-5 min', rollback_procedure: 'Re-deploy rolled-back version', last_executed: '2026-02-18T22:45:00Z', execution_count: 4, success_rate: 0.75 },
  { action_id: 'ACT-008', name: 'ElastiCache Flush (Selected Keys)', description: 'Flush stale key patterns.', trigger_condition: 'Cache poisoning detected', risk_level: 'high', requires_mfa: true, category: 'cache', estimated_duration: '1-2 min', rollback_procedure: 'Monitor hit rate', last_executed: '2026-02-26T12:00:00Z', execution_count: 3, success_rate: 1.0 },
];

export const DEMO_EXECUTIONS: ExecutionLogEntry[] = [
  { execution_id: 'exec-001', action_id: 'ACT-002', action_name: 'ECS Desired Count Scale-Out', investigation_id: 'inv-001', triggered_by: 'engineer@company.com', status: 'success', executed_at: '2026-02-27T11:20:00Z', duration_seconds: 187, pre_state: {}, post_state: {}, dry_run: false },
  { execution_id: 'exec-002', action_id: 'ACT-003', action_name: 'Lambda Concurrency Increase', investigation_id: 'inv-006', triggered_by: 'auto-remediation', status: 'success', executed_at: '2026-02-26T19:30:00Z', duration_seconds: 12, pre_state: {}, post_state: {}, dry_run: false },
  { execution_id: 'exec-003', action_id: 'ACT-008', action_name: 'ElastiCache Flush', investigation_id: 'inv-003', triggered_by: 'platform-lead@company.com', status: 'success', executed_at: '2026-02-26T12:00:00Z', duration_seconds: 45, pre_state: {}, post_state: {}, dry_run: false },
];

export const DEMO_EVAL_SUMMARY: EvalSummary = {
  last_updated: '2026-02-27T12:00:00Z',
  period: 'Last 30 days',
  kpis: [
    { name: 'Mean Time to Root Cause (MTTRC)', value: '4.2 min', target: '< 5 min', trend: 'improving', change: '-18% vs last month', status: 'on_track', history: [8.5, 7.2, 6.1, 5.5, 4.8, 4.2] },
    { name: 'Investigation Accuracy Rate', value: '87%', target: '≥ 85%', trend: 'improving', change: '+3% vs last month', status: 'on_track', history: [72, 76, 80, 82, 84, 87] },
    { name: 'Autonomous Coverage', value: '83%', target: '≥ 80%', trend: 'stable', change: '+1% vs last month', status: 'on_track', history: [65, 70, 75, 78, 82, 83] },
    { name: 'Alert-to-Investigation Latency', value: '2.8 min', target: '< 4 min', trend: 'improving', change: '-22% vs last month', status: 'on_track', history: [6.2, 5.1, 4.3, 3.8, 3.2, 2.8] },
    { name: 'On-Call Toil Reduction', value: '52%', target: '≥ 50%', trend: 'improving', change: '+8% vs last month', status: 'on_track', history: [15, 25, 33, 40, 44, 52] },
    { name: 'Auto-Remediation Success Rate', value: '94%', target: '≥ 90%', trend: 'stable', change: '+1% vs last month', status: 'on_track', history: [82, 85, 88, 91, 93, 94] },
    { name: 'False Positive Escalation Rate', value: '3.2%', target: '≤ 5%', trend: 'improving', change: '-1.5% vs last month', status: 'on_track', history: [12, 9, 7, 5.5, 4.7, 3.2] },
    { name: 'Engineer NPS', value: '42', target: '≥ 40', trend: 'improving', change: '+6 vs last month', status: 'on_track', history: [18, 24, 30, 34, 36, 42] },
  ],
  summary_stats: {
    total_investigations_30d: 127,
    auto_triggered: 105,
    manual_triggered: 22,
    avg_confidence: 0.84,
    total_remediations: 34,
    successful_remediations: 32,
    top_recurring_causes: [
      { cause: 'Connection pool exhaustion', count: 8 },
      { cause: 'Auto-scaling misconfiguration', count: 6 },
      { cause: 'Deployment-related regression', count: 5 },
      { cause: 'Third-party dependency outage', count: 4 },
    ],
  },
};

export const DEMO_FEEDBACK: FeedbackEntry[] = [
  { investigation_id: 'inv-001', rating: 'correct', comment: 'Spot on — connection pool was the issue.', submitted_by: 'sre-lead@company.com', submitted_at: '2026-02-27T12:00:00Z' },
  { investigation_id: 'inv-003', rating: 'correct', comment: 'Missing TTL was confirmed.', submitted_by: 'platform-eng@company.com', submitted_at: '2026-02-26T13:00:00Z' },
  { investigation_id: 'inv-005', rating: 'partially_correct', comment: 'Scaling config right; node group also needed update.', submitted_by: 'platform-eng@company.com', submitted_at: '2026-02-27T08:00:00Z' },
];

export const isDemoMode = () => process.env.NEXT_PUBLIC_USE_DEMO !== 'false';
