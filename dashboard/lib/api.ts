/**
 * API client — defaults to offline demo data for presentations
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
import {
  isDemoMode,
  getDemoInvestigationSummaries,
  getDemoInvestigationById,
  DEMO_SERVICES,
  DEMO_REMEDIATION_CATALOG,
  DEMO_EXECUTIONS,
  DEMO_EVAL_SUMMARY,
  DEMO_FEEDBACK,
} from './demo-data';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const FETCH_TIMEOUT_MS = 1500;

async function fetchApi<T>(path: string): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const response = await fetch(`${API_URL}${path}`, {
      cache: 'no-store',
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(response.statusText);
    return response.json();
  } finally {
    clearTimeout(timer);
  }
}

// ─── Investigations ──────────────────────────────────────────────────────────

export async function getInvestigations(params?: {
  status?: string;
  severity?: string;
  service?: string;
}): Promise<InvestigationSummary[]> {
  if (isDemoMode()) {
    let list = getDemoInvestigationSummaries();
    if (params?.status) list = list.filter((i) => i.status === params.status);
    if (params?.severity) list = list.filter((i) => i.severity === params.severity);
    if (params?.service) list = list.filter((i) => i.service === params.service);
    return list;
  }
  try {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set('status', params.status);
    if (params?.severity) searchParams.set('severity', params.severity);
    if (params?.service) searchParams.set('service', params.service);
    const query = searchParams.toString();
    return await fetchApi<InvestigationSummary[]>(`/investigations${query ? `?${query}` : ''}`);
  } catch {
    return getDemoInvestigationSummaries();
  }
}

export async function getInvestigation(id: string): Promise<Investigation> {
  if (isDemoMode()) {
    const inv = getDemoInvestigationById(id);
    if (!inv) throw new Error(`Investigation ${id} not found`);
    return inv;
  }
  try {
    return await fetchApi<Investigation>(`/investigations/${id}`);
  } catch (e) {
    const inv = getDemoInvestigationById(id);
    if (inv) return inv;
    throw e;
  }
}

export async function getInvestigationGraph(id: string): Promise<GraphData> {
  if (isDemoMode()) {
    return { nodes: [], edges: [] };
  }
  return fetchApi<GraphData>(`/investigations/${id}/graph`);
}

// ─── Services ────────────────────────────────────────────────────────────────

export async function getServices(): Promise<ServiceSummary[]> {
  if (isDemoMode()) return DEMO_SERVICES;
  try {
    return await fetchApi<ServiceSummary[]>('/services');
  } catch {
    return DEMO_SERVICES;
  }
}

export async function getService(name: string): Promise<ServiceDetail> {
  if (isDemoMode()) {
    const svc = DEMO_SERVICES.find((s) => s.name === name);
    if (!svc) throw new Error('Service not found');
    return { ...svc, dependencies: [], region: 'us-east-1', environment: 'production', incident_history: [] };
  }
  return fetchApi<ServiceDetail>(`/services/${name}`);
}

export async function getServiceHistory(name: string) {
  return fetchApi(`/services/${name}/history`);
}

// ─── Remediation ─────────────────────────────────────────────────────────────

export async function getRemediationCatalog(): Promise<RemediationAction[]> {
  if (isDemoMode()) return DEMO_REMEDIATION_CATALOG;
  try {
    return await fetchApi<RemediationAction[]>('/remediation/catalog');
  } catch {
    return DEMO_REMEDIATION_CATALOG;
  }
}

export async function getExecutionLog(): Promise<ExecutionLogEntry[]> {
  if (isDemoMode()) return DEMO_EXECUTIONS;
  try {
    return await fetchApi<ExecutionLogEntry[]>('/remediation/executions');
  } catch {
    return DEMO_EXECUTIONS;
  }
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
  if (isDemoMode()) return DEMO_EVAL_SUMMARY;
  try {
    return await fetchApi<EvalSummary>('/evals/summary');
  } catch {
    return DEMO_EVAL_SUMMARY;
  }
}

// ─── Feedback ────────────────────────────────────────────────────────────────

export async function getFeedback(): Promise<FeedbackEntry[]> {
  if (isDemoMode()) return DEMO_FEEDBACK;
  try {
    return await fetchApi<FeedbackEntry[]>('/feedback');
  } catch {
    return DEMO_FEEDBACK;
  }
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

export async function checkHealth() {
  if (isDemoMode()) return { status: 'ok', mode: 'demo' };
  return fetchApi('/health');
}
