import { getFeedback, getInvestigations } from '@/lib/api';
import { FeedbackEntry, InvestigationSummary } from '@/lib/types';

function RatingBadge({ rating }: { rating: string }) {
    const styles: Record<string, { bg: string; text: string; icon: string }> = {
        correct: { bg: 'bg-emerald-500/10 border-emerald-500/20', text: 'text-emerald-400', icon: '✅' },
        partially_correct: { bg: 'bg-amber-500/10 border-amber-500/20', text: 'text-amber-400', icon: '⚠️' },
        incorrect: { bg: 'bg-red-500/10 border-red-500/20', text: 'text-red-400', icon: '❌' },
    };
    const s = styles[rating] || styles.correct;
    return (
        <span className={`px-3 py-1 text-xs font-medium rounded-full border ${s.bg} ${s.text}`}>
            {s.icon} {rating.replace('_', ' ')}
        </span>
    );
}

export default async function FeedbackPage() {
    let feedback: FeedbackEntry[] = [];
    let investigations: InvestigationSummary[] = [];
    let error: string | null = null;

    try {
        [feedback, investigations] = await Promise.all([
            getFeedback(),
            getInvestigations(),
        ]);
    } catch (e) {
        error = e instanceof Error ? e.message : 'Failed to load feedback';
    }

    const correct = feedback.filter(f => f.rating === 'correct').length;
    const partial = feedback.filter(f => f.rating === 'partially_correct').length;
    const incorrect = feedback.filter(f => f.rating === 'incorrect').length;
    const total = feedback.length;
    const accuracyPct = total > 0 ? Math.round(((correct + partial * 0.5) / total) * 100) : 0;

    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white">Engineer Feedback</h1>
                <p className="mt-2 text-gray-500">
                    RCA accuracy ratings and corrections for continuous improvement
                </p>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6">
                    <p className="text-red-400">⚠ {error}</p>
                </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-5 gap-4 mb-8">
                {[
                    { label: 'Total Ratings', value: total, color: 'text-blue-400' },
                    { label: 'Correct', value: correct, color: 'text-emerald-400' },
                    { label: 'Partial', value: partial, color: 'text-amber-400' },
                    { label: 'Incorrect', value: incorrect, color: 'text-red-400' },
                    { label: 'Accuracy', value: `${accuracyPct}%`, color: accuracyPct >= 85 ? 'text-emerald-400' : 'text-amber-400' },
                ].map((stat) => (
                    <div key={stat.label} className="bg-gray-900 rounded-xl border border-gray-800 p-4">
                        <p className="text-xs text-gray-500 uppercase tracking-wide">{stat.label}</p>
                        <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
                    </div>
                ))}
            </div>

            {/* Accuracy Breakdown */}
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 mb-8">
                <h2 className="text-lg font-semibold text-white mb-4">Accuracy Distribution</h2>
                <div className="flex items-center gap-2 h-4 rounded-full overflow-hidden bg-gray-800">
                    {total > 0 && (
                        <>
                            <div className="bg-emerald-500 h-full rounded-l-full" style={{ width: `${(correct / total) * 100}%` }}></div>
                            <div className="bg-amber-500 h-full" style={{ width: `${(partial / total) * 100}%` }}></div>
                            <div className="bg-red-500 h-full rounded-r-full" style={{ width: `${(incorrect / total) * 100}%` }}></div>
                        </>
                    )}
                </div>
                <div className="flex justify-between mt-2 text-xs text-gray-500">
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-emerald-500 rounded-full"></span> Correct ({correct})</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-amber-500 rounded-full"></span> Partial ({partial})</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-red-500 rounded-full"></span> Incorrect ({incorrect})</span>
                </div>
            </div>

            {/* Feedback List */}
            <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-800">
                    <h2 className="text-lg font-semibold text-white">💬 Recent Feedback</h2>
                </div>
                <div className="divide-y divide-gray-800/50">
                    {feedback.map((entry, i) => {
                        const investigation = investigations.find(inv => inv.id === entry.investigation_id);
                        return (
                            <div key={i} className="px-6 py-4 hover:bg-gray-800/30 transition-colors">
                                <div className="flex justify-between items-start mb-2">
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-blue-400 font-mono text-sm">{entry.investigation_id}</span>
                                            {investigation && (
                                                <span className="text-gray-500 text-sm">— {investigation.title}</span>
                                            )}
                                        </div>
                                        <p className="text-gray-300 text-sm">&ldquo;{entry.comment}&rdquo;</p>
                                    </div>
                                    <RatingBadge rating={entry.rating} />
                                </div>
                                <div className="flex items-center gap-4 text-xs text-gray-600 mt-2">
                                    <span>By: {entry.submitted_by}</span>
                                    <span>{new Date(entry.submitted_at).toLocaleString()}</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
