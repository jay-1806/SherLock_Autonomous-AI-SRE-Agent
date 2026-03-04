import { getServices } from '@/lib/api';
import { ServiceSummary } from '@/lib/types';

function HealthBar({ score }: { score: number }) {
    const color = score >= 90 ? 'bg-emerald-400' : score >= 70 ? 'bg-amber-400' : 'bg-red-400';
    return (
        <div className="flex items-center gap-2">
            <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${score}%` }}></div>
            </div>
            <span className="text-xs text-gray-500 w-8 text-right">{score}</span>
        </div>
    );
}

function StatusDot({ status }: { status: string }) {
    const colors: Record<string, string> = {
        healthy: 'bg-emerald-400',
        degraded: 'bg-amber-400 animate-pulse',
        critical: 'bg-red-400 animate-pulse',
        unknown: 'bg-gray-400',
    };
    return <span className={`w-2.5 h-2.5 rounded-full inline-block ${colors[status] || colors.unknown}`}></span>;
}

export default async function ServicesPage() {
    let services: ServiceSummary[] = [];
    let error: string | null = null;

    try {
        services = await getServices();
    } catch (e) {
        error = e instanceof Error ? e.message : 'Failed to load services';
    }

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white">Service Health Map</h1>
                <p className="mt-2 text-gray-500">All monitored services with real-time health status</p>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6">
                    <p className="text-red-400">⚠ {error}</p>
                </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4 mb-8">
                {[
                    { label: 'Total Services', value: services.length, color: 'text-blue-400' },
                    { label: 'Healthy', value: services.filter(s => s.status === 'healthy').length, color: 'text-emerald-400' },
                    { label: 'Degraded', value: services.filter(s => s.status === 'degraded').length, color: 'text-amber-400' },
                    { label: 'Critical', value: services.filter(s => s.status === 'critical').length, color: 'text-red-400' },
                ].map((stat) => (
                    <div key={stat.label} className="bg-gray-900 rounded-xl border border-gray-800 p-4">
                        <p className="text-xs text-gray-500 uppercase tracking-wide">{stat.label}</p>
                        <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
                    </div>
                ))}
            </div>

            {/* Service Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {services.map((service) => (
                    <div
                        key={service.name}
                        className={`bg-gray-900 rounded-xl border p-5 card-hover ${service.status === 'critical' ? 'border-red-500/30 pulse-glow' :
                                service.status === 'degraded' ? 'border-amber-500/30' :
                                    'border-gray-800'
                            }`}
                    >
                        <div className="flex justify-between items-start mb-3">
                            <div className="flex items-center gap-2">
                                <StatusDot status={service.status} />
                                <h3 className="text-base font-semibold text-white">{service.display_name}</h3>
                            </div>
                            <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${service.sla_tier === 'P1' ? 'bg-red-500/10 text-red-400' :
                                    service.sla_tier === 'P2' ? 'bg-amber-500/10 text-amber-400' :
                                        'bg-gray-500/10 text-gray-500'
                                }`}>
                                {service.sla_tier}
                            </span>
                        </div>

                        <HealthBar score={service.health_score} />

                        <div className="grid grid-cols-2 gap-3 mt-4 text-xs">
                            <div>
                                <span className="text-gray-600">Team</span>
                                <p className="text-gray-400">{service.team}</p>
                            </div>
                            <div>
                                <span className="text-gray-600">Active Incidents</span>
                                <p className={service.active_incidents > 0 ? 'text-red-400 font-semibold' : 'text-gray-400'}>
                                    {service.active_incidents}
                                </p>
                            </div>
                            <div className="col-span-2">
                                <span className="text-gray-600">Last Deploy</span>
                                <p className="text-gray-400 font-mono">{new Date(service.last_deployment).toLocaleString()}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
