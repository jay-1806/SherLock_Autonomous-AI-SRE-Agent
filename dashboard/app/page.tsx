import { getInvestigations } from '@/lib/api';
import { InvestigationSummary } from '@/lib/types';
import Link from 'next/link';

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    open: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    in_progress: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    resolved: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    closed: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
  };
  return (
    <span className={`px-2.5 py-1 text-xs font-medium rounded-full border ${styles[status] || 'bg-gray-500/10 text-gray-400'}`}>
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
  const icons: Record<string, string> = {
    low: '○', medium: '◑', high: '◉', critical: '●',
  };
  return (
    <span className={`px-2.5 py-1 text-xs font-medium rounded-full flex items-center gap-1 ${styles[severity] || ''}`}>
      <span>{icons[severity]}</span> {severity}
    </span>
  );
}

function ConfidenceMeter({ confidence }: { confidence?: number }) {
  if (!confidence) return null;
  const pct = Math.round(confidence * 100);
  const color = pct >= 85 ? 'bg-emerald-400' : pct >= 70 ? 'bg-amber-400' : 'bg-red-400';
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }}></div>
      </div>
      <span className="text-xs text-gray-500">{pct}%</span>
    </div>
  );
}

function InvestigationCard({ investigation }: { investigation: InvestigationSummary }) {
  const time = new Date(investigation.created_at).toLocaleString();
  const isActive = investigation.status === 'open' || investigation.status === 'in_progress';

  return (
    <Link href={`/investigations/${investigation.id}`}>
      <div className={`bg-gray-900 rounded-xl border border-gray-800 p-5 card-hover cursor-pointer ${isActive ? 'pulse-glow' : ''}`}>
        <div className="flex justify-between items-start mb-3">
          <h3 className="text-base font-semibold text-white leading-tight">{investigation.title}</h3>
          <SeverityBadge severity={investigation.severity} />
        </div>
        {investigation.rca_summary && (
          <p className="text-xs text-gray-500 mb-3 line-clamp-2">{investigation.rca_summary}</p>
        )}
        <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
          <span className="font-mono bg-gray-800 px-2 py-0.5 rounded text-gray-400">{investigation.service}</span>
          <span>•</span>
          <span>{time}</span>
        </div>
        <div className="flex justify-between items-center">
          <StatusBadge status={investigation.status} />
          <ConfidenceMeter confidence={investigation.confidence} />
        </div>
      </div>
    </Link>
  );
}

export default async function HomePage() {
  const investigations = await getInvestigations();

  const active = investigations.filter(i => i.status === 'open' || i.status === 'in_progress');
  const resolved = investigations.filter(i => i.status === 'resolved' || i.status === 'closed');

  return (
    <div>
      <div className="mb-8 space-y-6">
        <div className="rounded-2xl border border-emerald-500/20 bg-gradient-to-r from-emerald-500/10 via-cyan-500/10 to-transparent p-6">
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-300 mb-3 block">Autonomous SRE Agent</span>
          <h1 className="text-3xl font-bold text-white">SherLock Incident Command Center</h1>
          <p className="mt-2 text-gray-300 max-w-3xl">
            AI-powered investigation feed with confidence-scored RCA, blast radius, and remediation recommendations.
          </p>
          <div className="flex flex-wrap gap-3 mt-5">
            <Link href="/investigations/inv-002" className="px-3 py-2 text-sm rounded-lg bg-red-500/20 text-red-300 border border-red-400/30 hover:bg-red-500/30 transition-colors">
              Open critical incident →
            </Link>
            <Link href="/kpis" className="px-3 py-2 text-sm rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors">
              View KPIs
            </Link>
            <Link href="/remediation" className="px-3 py-2 text-sm rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 hover:bg-emerald-500/30 transition-colors">
              Remediation center
            </Link>
          </div>
        </div>

        <p className="text-gray-500">
          Active and recent investigations • {investigations.length} total
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Active', value: active.length, color: 'text-amber-400' },
          { label: 'Critical', value: investigations.filter(i => i.severity === 'critical').length, color: 'text-red-400' },
          { label: 'Resolved', value: resolved.length, color: 'text-emerald-400' },
          { label: 'Avg Confidence', value: investigations.length ? Math.round(investigations.reduce((a, i) => a + (i.confidence || 0), 0) / investigations.length * 100) + '%' : 'N/A', color: 'text-blue-400' },
        ].map((stat) => (
          <div key={stat.label} className="bg-gray-900/85 backdrop-blur rounded-xl border border-gray-800 p-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide">{stat.label}</p>
            <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      {active.length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-amber-400 rounded-full animate-pulse"></span>
            Active Investigations
          </h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {active.map((inv) => (
              <InvestigationCard key={inv.id} investigation={inv} />
            ))}
          </div>
        </div>
      )}

      {resolved.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-400 mb-4">Resolved</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {resolved.map((inv) => (
              <InvestigationCard key={inv.id} investigation={inv} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
