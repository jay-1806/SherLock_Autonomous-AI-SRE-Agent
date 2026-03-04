import { getInvestigation } from '@/lib/api';
import { Investigation } from '@/lib/types';
import Link from 'next/link';
import { notFound } from 'next/navigation';

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    open: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    in_progress: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    resolved: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    closed: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
  };
  return (
    <span className={`px-3 py-1 text-sm font-medium rounded-full border ${styles[status] || 'bg-gray-500/10'}`}>
      {status.replace('_', ' ')}
    </span>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  const styles: Record<string, string> = {
    low: 'bg-gray-500/10 text-gray-400',
    medium: 'bg-yellow-500/10 text-yellow-400',
    high: 'bg-orange-500/10 text-orange-400',
    critical: 'bg-red-500/10 text-red-400',
  };
  return (
    <span className={`px-3 py-1 text-sm font-medium rounded-full ${styles[severity] || ''}`}>
      {severity.toUpperCase()}
    </span>
  );
}

function ConfidenceRing({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100);
  const color = pct >= 85 ? 'text-emerald-400' : pct >= 70 ? 'text-amber-400' : 'text-red-400';
  const bgColor = pct >= 85 ? 'bg-emerald-400' : pct >= 70 ? 'bg-amber-400' : 'bg-red-400';
  return (
    <div className="flex items-center gap-3 bg-gray-800/50 rounded-xl px-4 py-3">
      <div className="relative w-12 h-12">
        <svg className="w-12 h-12 -rotate-90" viewBox="0 0 36 36">
          <path d="M18 2.0845a16 16 0 0 1 0 31.831 16 16 0 0 1 0-31.831" fill="none" stroke="#374151" strokeWidth="3" />
          <path d="M18 2.0845a16 16 0 0 1 0 31.831 16 16 0 0 1 0-31.831" fill="none" stroke="currentColor" strokeWidth="3" strokeDasharray={`${pct}, 100`} className={color} />
        </svg>
        <span className={`absolute inset-0 flex items-center justify-center text-xs font-bold ${color}`}>{pct}%</span>
      </div>
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wide">Confidence</p>
        <p className={`text-sm font-semibold ${color}`}>
          {pct >= 85 ? 'High' : pct >= 70 ? 'Medium' : 'Low'}
        </p>
      </div>
    </div>
  );
}

function Timeline({ events }: { events: Investigation['timeline'] }) {
  if (!events || events.length === 0) {
    return <p className="text-gray-500">No timeline events yet</p>;
  }
  return (
    <div className="space-y-0">
      {events.map((event, index) => {
        const time = new Date(event.timestamp).toLocaleTimeString();
        const sourceColors: Record<string, string> = {
          sherlock: 'bg-emerald-500', pagerduty: 'bg-yellow-500', datadog: 'bg-purple-500',
          cloudwatch: 'bg-orange-500', prometheus: 'bg-red-500', manual: 'bg-blue-500',
          external: 'bg-gray-500',
        };
        const dotColor = sourceColors[event.source] || 'bg-gray-500';
        return (
          <div key={index} className="flex gap-4 group">
            <div className="flex flex-col items-center">
              <div className={`w-2.5 h-2.5 rounded-full ${dotColor} mt-1.5 ring-4 ring-gray-900`}></div>
              {index < events.length - 1 && <div className="w-px flex-1 bg-gray-800 my-1"></div>}
            </div>
            <div className="pb-5">
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-xs text-gray-600 font-mono">{time}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded ${dotColor}/10 text-gray-400`}>{event.source}</span>
              </div>
              <p className="text-sm text-gray-300">{event.event}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default async function InvestigationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let investigation: Investigation | null = null;
  let error: string | null = null;

  try {
    investigation = await getInvestigation(id);
  } catch (e) {
    if (e instanceof Error && e.message.includes('not found')) notFound();
    error = e instanceof Error ? e.message : 'Failed to load investigation';
  }

  if (error) {
    return (
      <div>
        <Link href="/" className="text-emerald-400 hover:text-emerald-300 mb-4 inline-block text-sm">← Back to Incidents</Link>
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
          <p className="text-red-400">Error: {error}</p>
        </div>
      </div>
    );
  }

  if (!investigation) notFound();

  return (
    <div>
      <Link href="/" className="text-emerald-400 hover:text-emerald-300 mb-6 inline-block text-sm">← Back to Incidents</Link>

      {/* Header */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-2xl font-bold text-white">{investigation.title}</h1>
            <p className="text-gray-500 text-sm mt-1 font-mono">{investigation.id}</p>
          </div>
          <div className="flex gap-2">
            <StatusBadge status={investigation.status} />
            <SeverityBadge severity={investigation.severity} />
          </div>
        </div>
        <p className="text-gray-400 mb-6">{investigation.description}</p>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div>
            <p className="text-xs text-gray-600 uppercase tracking-wide">Service</p>
            <p className="font-mono bg-gray-800 px-2 py-1 rounded text-gray-300 text-sm mt-1 inline-block">{investigation.service}</p>
          </div>
          <div>
            <p className="text-xs text-gray-600 uppercase tracking-wide">Assigned</p>
            <p className="text-gray-300 text-sm mt-1">{investigation.assigned_to || 'Unassigned'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-600 uppercase tracking-wide">Created</p>
            <p className="text-gray-300 text-sm mt-1">{new Date(investigation.created_at).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs text-gray-600 uppercase tracking-wide">Updated</p>
            <p className="text-gray-300 text-sm mt-1">{new Date(investigation.updated_at).toLocaleString()}</p>
          </div>
          {investigation.confidence && <ConfidenceRing confidence={investigation.confidence} />}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          {/* Root Cause */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
            <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">🎯 Root Cause</h2>
            {investigation.root_cause ? (
              <p className="text-gray-300">{investigation.root_cause}</p>
            ) : (
              <p className="text-gray-600 italic">Root cause under investigation...</p>
            )}
          </div>

          {/* Hypotheses */}
          {investigation.hypotheses && investigation.hypotheses.length > 0 && (
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-semibold text-white mb-3">🧪 Hypotheses</h2>
              <div className="space-y-3">
                {investigation.hypotheses.map((h, i) => {
                  const statusIcon = h.status === 'confirmed' ? '✅' : h.status === 'rejected' ? '❌' : '🔄';
                  const pct = Math.round(h.confidence * 100);
                  return (
                    <div key={i} className="flex items-center justify-between bg-gray-800/50 rounded-lg px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span>{statusIcon}</span>
                        <span className="text-sm text-gray-300">{h.hypothesis}</span>
                      </div>
                      <span className="text-xs text-gray-500 font-mono">{pct}%</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Evidence */}
          {investigation.evidence && investigation.evidence.length > 0 && (
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-semibold text-white mb-3">📋 Evidence</h2>
              <div className="space-y-3">
                {investigation.evidence.map((e, i) => (
                  <div key={i} className="border-l-2 border-blue-500/30 pl-4 py-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded">{e.type}</span>
                      <span className="text-xs text-gray-600">{e.source}</span>
                    </div>
                    <p className="text-sm text-gray-400">{e.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Timeline */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
            <h2 className="text-lg font-semibold text-white mb-4">📍 Timeline</h2>
            <Timeline events={investigation.timeline} />
          </div>

          {/* Blast Radius */}
          {investigation.blast_radius && investigation.blast_radius.length > 0 && (
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-semibold text-white mb-3">💥 Blast Radius</h2>
              <div className="flex flex-wrap gap-2">
                {investigation.blast_radius.map((svc) => (
                  <span key={svc} className="bg-amber-500/10 text-amber-400 border border-amber-500/20 px-3 py-1.5 rounded-lg text-sm font-mono">
                    {svc}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Remediation */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
            <h2 className="text-lg font-semibold text-white mb-3">⚡ Remediation</h2>
            {investigation.remediation ? (
              <div>
                <p className="text-gray-300 mb-3">{investigation.remediation}</p>
                {investigation.nba_action_id && (
                  <Link
                    href="/remediation"
                    className="inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-500/20 transition-colors"
                  >
                    ⚡ View Recommended Action: {investigation.nba_action_id}
                  </Link>
                )}
              </div>
            ) : (
              <p className="text-gray-600 italic">No remediation steps defined yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
