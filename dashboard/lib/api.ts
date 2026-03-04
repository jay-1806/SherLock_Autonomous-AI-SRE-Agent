/**
 * API client for SherLock backend
 */

import {
  Investigation,
  InvestigationSummary,
  ServiceSummary,
  ServiceDetail,
  RemediationAction,
  ExecutionLogEntry,
  EvalSummary,
  FeedbackEntry,
  GraphData,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ─── Investigations ──────────────────────────────────────────────────────────

export async function getInvestigations(params?: {
  status?: string;
  severity?: string;
  service?: string;
}): Promise<InvestigationSummary[]> {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set('status', params.status);
  if (params?.severity) searchParams.set('severity', params.severity);
  if (params?.service) searchParams.set('service', params.service);

  const query = searchParams.toString();
  const url = `${API_URL}/investigations${query ? `?${query}` : ''}`;

  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Failed to fetch investigations: ${response.statusText}`);
  return response.json();
}

export async function getInvestigation(id: string): Promise<Investigation> {
  const response = await fetch(`${API_URL}/investigations/${id}`, { cache: 'no-store' });
  if (!response.ok) {
    if (response.status === 404) throw new Error(`Investigation ${id} not found`);
    throw new Error(`Failed to fetch investigation: ${response.statusText}`);
  }
  return response.json();
}

export async function getInvestigationGraph(id: string): Promise<GraphData> {
  const response = await fetch(`${API_URL}/investigations/${id}/graph`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Failed to fetch graph: ${response.statusText}`);
  return response.json();
}

// ─── Services ────────────────────────────────────────────────────────────────

export async function getServices(): Promise<ServiceSummary[]> {
  const response = await fetch(`${API_URL}/services`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Failed to fetch services: ${response.statusText}`);
  return response.json();
}

export async function getService(name: string): Promise<ServiceDetail> {
  const response = await fetch(`${API_URL}/services/${name}`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Failed to fetch service: ${response.statusText}`);
  return response.json();
}

export async function getServiceHistory(name: string) {
  const response = await fetch(`${API_URL}/services/${name}/history`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Failed to fetch service history: ${response.statusText}`);
  return response.json();
}

// ─── Remediation ─────────────────────────────────────────────────────────────

export async function getRemediationCatalog(): Promise<RemediationAction[]> {
  const response = await fetch(`${API_URL}/remediation/catalog`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Failed to fetch catalog: ${response.statusText}`);
  return response.json();
}

export async function getExecutionLog(): Promise<ExecutionLogEntry[]> {
  const response = await fetch(`${API_URL}/remediation/executions`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Failed to fetch executions: ${response.statusText}`);
  return response.json();
}

export async function executeRemediation(actionId: string, investigationId: string, dryRun = false) {
  const response = await fetch(`${API_URL}/remediation/${actionId}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ investigation_id: investigationId, dry_run: dryRun }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Execution failed');
  }
  return response.json();
}

// ─── Evals & KPIs ────────────────────────────────────────────────────────────

export async function getEvalSummary(): Promise<EvalSummary> {
  const response = await fetch(`${API_URL}/evals/summary`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Failed to fetch eval summary: ${response.statusText}`);
  return response.json();
}

// ─── Feedback ────────────────────────────────────────────────────────────────

export async function getFeedback(): Promise<FeedbackEntry[]> {
  const response = await fetch(`${API_URL}/feedback`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Failed to fetch feedback: ${response.statusText}`);
  return response.json();
}

export async function submitFeedback(investigationId: string, rating: string, comment?: string) {
  const response = await fetch(`${API_URL}/feedback/${investigationId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rating, comment, submitted_by: 'dashboard-user' }),
  });
  if (!response.ok) throw new Error(`Failed to submit feedback: ${response.statusText}`);
  return response.json();
}

// ─── Health ──────────────────────────────────────────────────────────────────

export async function checkHealth() {
  const response = await fetch(`${API_URL}/health`, { cache: 'no-store' });
  if (!response.ok) throw new Error('API health check failed');
  return response.json();
}
