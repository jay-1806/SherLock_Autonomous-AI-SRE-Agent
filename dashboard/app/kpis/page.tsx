import { getEvalSummary } from '@/lib/api';
import { EvalSummary } from '@/lib/types';

function Sparkline({ data, color }: { data: number[]; color: string }) {
    if (!data || data.length === 0) return null;
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;
    return (
        <div className="flex items-end gap-[2px] h-8">
            {data.map((v, i) => {
                const height = Math.max(4, ((v - min) / range) * 100);
                return (
                    <div
                        key={i}
                        className={`w-1.5 rounded-sm ${color} ${i === data.length - 1 ? 'opacity-100' : 'opacity-50'}`}
                        style={{ height: `${height}%` }}
                    ></div>
                );
            })}
        </div>
    );
}

function TrendArrow({ trend }: { trend: string }) {
    if (trend === 'improving') return <span className="text-emerald-400">↑</span>;
    if (trend === 'declining') return <span className="text-red-400">↓</span>;
    return <span className="text-gray-500">→</span>;
}

export default async function KPIsPage() {
    let data: EvalSummary | null = null;
    let error: string | null = null;

    try {
        data = await getEvalSummary();
    } catch (e) {
        error = e instanceof Error ? e.message : 'Failed to load KPIs';
    }

    const sparkColors: Record<string, string> = {
        'Mean Time to Root Cause (MTTRC)': 'bg-blue-400',
        'Investigation Accuracy Rate': 'bg-emerald-400',
        'Autonomous Coverage': 'bg-purple-400',
        'Alert-to-Investigation Latency': 'bg-cyan-400',
        'On-Call Toil Reduction': 'bg-amber-400',
        'Auto-Remediation Success Rate': 'bg-emerald-400',
        'False Positive Escalation Rate': 'bg-red-400',
        'Engineer NPS': 'bg-pink-400',
    };

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white">KPI Dashboard</h1>
                <p className="mt-2 text-gray-500">
                    Platform performance metrics and trends
                    {data && <span className="text-gray-600"> • {data.period} • Updated {new Date(data.last_updated).toLocaleString()}</span>}
                </p>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6">
                    <p className="text-red-400">⚠ {error}</p>
                </div>
            )}

            {data && (
                <>
                    {/* KPI Cards */}
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
                        {data.kpis.map((kpi) => (
                            <div key={kpi.name} className="bg-gray-900 rounded-xl border border-gray-800 p-5 card-hover">
                                <div className="flex justify-between items-start mb-3">
                                    <p className="text-xs text-gray-500 uppercase tracking-wide leading-tight">{kpi.name}</p>
                                    <TrendArrow trend={kpi.trend} />
                                </div>
                                <div className="flex items-end justify-between mb-3">
                                    <p className="text-3xl font-bold text-white">{kpi.value}</p>
                                    <Sparkline data={kpi.history} color={sparkColors[kpi.name] || 'bg-blue-400'} />
                                </div>
                                <div className="flex justify-between items-center">
                                    <p className="text-xs text-gray-600">Target: {kpi.target}</p>
                                    <span className={`text-xs px-2 py-0.5 rounded ${kpi.status === 'on_track' ? 'bg-emerald-500/10 text-emerald-400' :
                                            kpi.status === 'at_risk' ? 'bg-amber-500/10 text-amber-400' :
                                                'bg-red-500/10 text-red-400'
                                        }`}>
                                        {kpi.status === 'on_track' ? '✓ On Track' : kpi.status}
                                    </span>
                                </div>
                                <p className="text-xs text-gray-600 mt-2">{kpi.change}</p>
                            </div>
                        ))}
                    </div>

                    {/* Summary Stats */}
                    <div className="grid gap-6 md:grid-cols-2">
                        {/* Investigation Stats */}
                        <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
                            <h2 className="text-lg font-semibold text-white mb-4">📊 Investigation Summary (30d)</h2>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-400">Total Investigations</span>
                                    <span className="text-white font-semibold">{data.summary_stats.total_investigations_30d}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-400">Auto-Triggered</span>
                                    <div className="flex items-center gap-2">
                                        <span className="text-white font-semibold">{data.summary_stats.auto_triggered}</span>
                                        <span className="text-xs text-emerald-400">
                                            ({Math.round(data.summary_stats.auto_triggered / data.summary_stats.total_investigations_30d * 100)}%)
                                        </span>
                                    </div>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-400">Manual Triggered</span>
                                    <span className="text-white font-semibold">{data.summary_stats.manual_triggered}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-400">Avg Confidence</span>
                                    <span className="text-white font-semibold">{(data.summary_stats.avg_confidence * 100).toFixed(0)}%</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm text-gray-400">Remediations (Success/Total)</span>
                                    <span className="text-emerald-400 font-semibold">
                                        {data.summary_stats.successful_remediations}/{data.summary_stats.total_remediations}
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Top Recurring Causes */}
                        <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
                            <h2 className="text-lg font-semibold text-white mb-4">🔄 Top Recurring Root Causes</h2>
                            <div className="space-y-3">
                                {data.summary_stats.top_recurring_causes.map((cause, i) => (
                                    <div key={i} className="flex items-center gap-3">
                                        <span className="text-xs text-gray-600 w-5">{i + 1}.</span>
                                        <div className="flex-1">
                                            <div className="flex justify-between items-center mb-1">
                                                <span className="text-sm text-gray-300">{cause.cause}</span>
                                                <span className="text-xs text-gray-500">{cause.count} incidents</span>
                                            </div>
                                            <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-blue-500/50 rounded-full"
                                                    style={{ width: `${(cause.count / data!.summary_stats.top_recurring_causes[0].count) * 100}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
