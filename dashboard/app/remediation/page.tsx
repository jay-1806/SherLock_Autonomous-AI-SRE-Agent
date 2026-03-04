import { getRemediationCatalog, getExecutionLog } from '@/lib/api';
import { RemediationAction, ExecutionLogEntry } from '@/lib/types';

function RiskBadge({ level }: { level: string }) {
    const styles: Record<string, string> = {
        low: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
        medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
        high: 'bg-red-500/10 text-red-400 border-red-500/20',
    };
    return (
        <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${styles[level] || ''}`}>
            {level}
        </span>
    );
}

export default async function RemediationPage() {
    let catalog: RemediationAction[] = [];
    let executions: ExecutionLogEntry[] = [];
    let error: string | null = null;

    try {
        [catalog, executions] = await Promise.all([
            getRemediationCatalog(),
            getExecutionLog(),
        ]);
    } catch (e) {
        error = e instanceof Error ? e.message : 'Failed to load data';
    }

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white">Remediation Center</h1>
                <p className="mt-2 text-gray-500">Pre-approved auto-remediation actions and execution history</p>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6">
                    <p className="text-red-400">⚠ {error}</p>
                </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4 mb-8">
                {[
                    { label: 'Catalog Actions', value: catalog.length, color: 'text-blue-400' },
                    { label: 'Total Executions', value: executions.length, color: 'text-purple-400' },
                    { label: 'Success Rate', value: '94%', color: 'text-emerald-400' },
                    { label: 'MFA Required', value: catalog.filter(a => a.requires_mfa).length, color: 'text-amber-400' },
                ].map((stat) => (
                    <div key={stat.label} className="bg-gray-900 rounded-xl border border-gray-800 p-4">
                        <p className="text-xs text-gray-500 uppercase tracking-wide">{stat.label}</p>
                        <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
                    </div>
                ))}
            </div>

            {/* Action Catalog */}
            <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden mb-8">
                <div className="px-6 py-4 border-b border-gray-800">
                    <h2 className="text-lg font-semibold text-white">⚡ Action Catalog</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="text-xs text-gray-500 uppercase tracking-wide border-b border-gray-800">
                                <th className="text-left px-6 py-3">ID</th>
                                <th className="text-left px-6 py-3">Action</th>
                                <th className="text-left px-6 py-3">Category</th>
                                <th className="text-left px-6 py-3">Risk</th>
                                <th className="text-left px-6 py-3">MFA</th>
                                <th className="text-left px-6 py-3">Executions</th>
                                <th className="text-left px-6 py-3">Success</th>
                                <th className="text-left px-6 py-3">Duration</th>
                            </tr>
                        </thead>
                        <tbody>
                            {catalog.map((action) => (
                                <tr key={action.action_id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                                    <td className="px-6 py-4 font-mono text-emerald-400 text-xs">{action.action_id}</td>
                                    <td className="px-6 py-4">
                                        <div>
                                            <p className="text-white font-medium">{action.name}</p>
                                            <p className="text-gray-600 text-xs mt-0.5 max-w-xs truncate">{action.trigger_condition}</p>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="bg-gray-800 text-gray-400 px-2 py-0.5 rounded text-xs">{action.category}</span>
                                    </td>
                                    <td className="px-6 py-4"><RiskBadge level={action.risk_level} /></td>
                                    <td className="px-6 py-4 text-center">{action.requires_mfa ? '🔐' : '—'}</td>
                                    <td className="px-6 py-4 text-gray-400">{action.execution_count}</td>
                                    <td className="px-6 py-4">
                                        {action.success_rate !== null ? (
                                            <span className={action.success_rate >= 0.9 ? 'text-emerald-400' : 'text-amber-400'}>
                                                {Math.round(action.success_rate * 100)}%
                                            </span>
                                        ) : (
                                            <span className="text-gray-600">—</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 text-gray-500 text-xs">{action.estimated_duration}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Execution Log */}
            <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-800">
                    <h2 className="text-lg font-semibold text-white">📋 Execution History</h2>
                </div>
                <div className="divide-y divide-gray-800/50">
                    {executions.map((exec) => (
                        <div key={exec.execution_id} className="px-6 py-4 hover:bg-gray-800/30 transition-colors">
                            <div className="flex justify-between items-start">
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={`w-2 h-2 rounded-full ${exec.status === 'success' ? 'bg-emerald-400' : 'bg-red-400'}`}></span>
                                        <span className="text-white font-medium text-sm">{exec.action_name}</span>
                                        <span className="text-gray-600 text-xs font-mono">{exec.action_id}</span>
                                    </div>
                                    <p className="text-xs text-gray-500">
                                        Investigation: <span className="text-blue-400">{exec.investigation_id}</span>
                                        {' • '}Triggered by: <span className="text-gray-400">{exec.triggered_by}</span>
                                        {' • '}Duration: <span className="text-gray-400">{exec.duration_seconds}s</span>
                                    </p>
                                </div>
                                <div className="text-right">
                                    <p className="text-xs text-gray-600">{new Date(exec.executed_at).toLocaleString()}</p>
                                    <span className={`text-xs px-2 py-0.5 rounded ${exec.status === 'success' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                                        {exec.status}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
