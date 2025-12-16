import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
    BarChart3, TrendingUp, Users, Target, Zap, RefreshCw, 
    Loader2, ChevronLeft, PieChart, Activity, Calendar,
    ArrowUp, ArrowDown, Minus
} from 'lucide-react';

const API_URL = 'https://apex-backend-i7b0.onrender.com';

interface AnalyticsData {
    total_contacts: number;
    enriched_contacts: number;
    scored_contacts: number;
    tier_distribution: {
        HIGH: number;
        MEDIUM: number;
        LOW: number;
        MINIMAL: number;
    };
    avg_scores: {
        match: number;
        fit: number;
        relevance: number;
        timing: number;
    };
    enrichment_rate: number;
    top_companies: { company: string; count: number; avg_score: number }[];
    recent_activity: { date: string; enriched: number; scored: number }[];
    cold_call_stats: {
        total: number;
        new: number;
        attempted: number;
        connected: number;
        meeting_set: number;
        conversion_rate: number;
    };
}

export default function Analytics() {
    const [data, setData] = useState<AnalyticsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [timeRange, setTimeRange] = useState<'7d' | '30d' | 'all'>('all');

    useEffect(() => {
        fetchAnalytics();
    }, [timeRange]);

    const fetchAnalytics = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${API_URL}/api/analytics?range=${timeRange}`);
            const json = await res.json();
            // Normalize API response to expected format
            const normalized = {
                total_contacts: json.total_contacts || json.contacts?.total || 0,
                enriched_contacts: json.enriched_contacts || json.contacts?.enriched || 0,
                scored_contacts: json.scored_contacts || json.contacts?.scored || 0,
                enrichment_rate: json.enrichment_rate || json.contacts?.enrichment_rate || 0,
                tier_distribution: json.tier_distribution || json.match_tiers || { HIGH: 0, MEDIUM: 0, LOW: 0, MINIMAL: 0 },
                avg_scores: json.avg_scores || { match: 0, fit: 0, relevance: 0, timing: 0 },
                top_companies: json.top_companies || [],
                recent_activity: json.recent_activity || [],
                cold_call_stats: json.cold_call_stats || { total: 0, new: 0, attempted: 0, connected: 0, meeting_set: 0, conversion_rate: 0 }
            };
            setData(normalized);
        } catch (e) {
            console.error('Analytics fetch error:', e);
        } finally {
            setLoading(false);
        }
    };

    const StatCard = ({ 
        label, value, subvalue, icon, color = 'text-white', trend 
    }: { 
        label: string; 
        value: string | number; 
        subvalue?: string;
        icon: React.ReactNode; 
        color?: string;
        trend?: 'up' | 'down' | 'flat';
    }) => (
        <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-gray-400 text-sm mb-1">{label}</p>
                    <p className={`text-3xl font-bold ${color}`}>{value}</p>
                    {subvalue && <p className="text-gray-500 text-sm mt-1">{subvalue}</p>}
                </div>
                <div className={`p-3 rounded-lg bg-gray-800 ${color}`}>
                    {icon}
                </div>
            </div>
            {trend && (
                <div className="mt-3 flex items-center gap-1 text-sm">
                    {trend === 'up' && <ArrowUp size={14} className="text-green-400" />}
                    {trend === 'down' && <ArrowDown size={14} className="text-red-400" />}
                    {trend === 'flat' && <Minus size={14} className="text-gray-400" />}
                    <span className={trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-gray-400'}>
                        {trend === 'up' ? 'Trending up' : trend === 'down' ? 'Trending down' : 'Stable'}
                    </span>
                </div>
            )}
        </div>
    );

    const TierBar = ({ tier, count, total, color }: { tier: string; count: number; total: number; color: string }) => {
        const pct = total > 0 ? (count / total) * 100 : 0;
        return (
            <div className="flex items-center gap-3">
                <span className="w-20 text-sm text-gray-400">{tier}</span>
                <div className="flex-1 h-8 bg-gray-800 rounded-lg overflow-hidden">
                    <div 
                        className={`h-full ${color} flex items-center justify-end pr-3 transition-all duration-500`}
                        style={{ width: `${Math.max(pct, 5)}%` }}
                    >
                        <span className="text-white text-sm font-bold">{count}</span>
                    </div>
                </div>
                <span className="w-16 text-right text-sm text-gray-500">{pct.toFixed(1)}%</span>
            </div>
        );
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#0f1114] flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
            </div>
        );
    }

    const tierTotal = data?.tier_distribution ? 
        ((data.tier_distribution.HIGH || 0) + (data.tier_distribution.MEDIUM || 0) + 
         (data.tier_distribution.LOW || 0) + (data.tier_distribution.MINIMAL || 0)) : 0;

    return (
        <div className="min-h-screen bg-[#0f1114] text-white">
            {/* Header */}
            <div className="bg-[#1a1d21] border-b border-gray-800 px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link to="/" className="text-gray-400 hover:text-white flex items-center gap-1">
                            <ChevronLeft size={20} /> Dashboard
                        </Link>
                        <h1 className="text-2xl font-bold flex items-center gap-2">
                            <BarChart3 className="text-purple-400" /> Pipeline Analytics
                        </h1>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="bg-[#0f1114] rounded-lg p-1 flex">
                            {(['7d', '30d', 'all'] as const).map(range => (
                                <button
                                    key={range}
                                    onClick={() => setTimeRange(range)}
                                    className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                                        timeRange === range ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'
                                    }`}
                                >
                                    {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : 'All Time'}
                                </button>
                            ))}
                        </div>
                        <button onClick={fetchAnalytics} className="p-2 hover:bg-gray-800 rounded-lg">
                            <RefreshCw size={20} className="text-gray-400" />
                        </button>
                    </div>
                </div>
            </div>

            <div className="p-6 space-y-6">
                {/* Top Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <StatCard
                        label="Total Contacts"
                        value={data?.total_contacts || 0}
                        icon={<Users size={24} />}
                        color="text-blue-400"
                    />
                    <StatCard
                        label="Enriched"
                        value={data?.enriched_contacts || 0}
                        subvalue={`${data?.enrichment_rate?.toFixed(1) || 0}% rate`}
                        icon={<Zap size={24} />}
                        color="text-purple-400"
                    />
                    <StatCard
                        label="Avg Match Score"
                        value={data?.avg_scores?.match?.toFixed(1) || 0}
                        icon={<Target size={24} />}
                        color="text-green-400"
                    />
                    <StatCard
                        label="High Priority"
                        value={data?.tier_distribution?.HIGH || 0}
                        subvalue="Ready to contact"
                        icon={<TrendingUp size={24} />}
                        color="text-yellow-400"
                        trend="up"
                    />
                </div>

                <div className="grid lg:grid-cols-2 gap-6">
                    {/* Tier Distribution */}
                    <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                        <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                            <PieChart size={18} className="text-purple-400" /> Match Tier Distribution
                        </h3>
                        <div className="space-y-3">
                            <TierBar tier="HIGH" count={data?.tier_distribution?.HIGH || 0} total={tierTotal} color="bg-green-500" />
                            <TierBar tier="MEDIUM" count={data?.tier_distribution?.MEDIUM || 0} total={tierTotal} color="bg-yellow-500" />
                            <TierBar tier="LOW" count={data?.tier_distribution?.LOW || 0} total={tierTotal} color="bg-orange-500" />
                            <TierBar tier="MINIMAL" count={data?.tier_distribution?.MINIMAL || 0} total={tierTotal} color="bg-red-500" />
                        </div>
                    </div>

                    {/* Score Breakdown */}
                    <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                        <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                            <Activity size={18} className="text-blue-400" /> Average Score Breakdown
                        </h3>
                        <div className="grid grid-cols-3 gap-4">
                            <div className="text-center p-4 bg-[#0f1114] rounded-lg">
                                <p className="text-3xl font-bold text-green-400">{data?.avg_scores?.fit?.toFixed(1) || 0}</p>
                                <p className="text-gray-500 text-sm mt-1">FIT</p>
                                <p className="text-gray-600 text-xs">Title & Company</p>
                            </div>
                            <div className="text-center p-4 bg-[#0f1114] rounded-lg">
                                <p className="text-3xl font-bold text-blue-400">{data?.avg_scores?.relevance?.toFixed(1) || 0}</p>
                                <p className="text-gray-500 text-sm mt-1">RELEVANCE</p>
                                <p className="text-gray-600 text-xs">Pain ↔ Solution</p>
                            </div>
                            <div className="text-center p-4 bg-[#0f1114] rounded-lg">
                                <p className="text-3xl font-bold text-orange-400">{data?.avg_scores?.timing?.toFixed(1) || 0}</p>
                                <p className="text-gray-500 text-sm mt-1">TIMING</p>
                                <p className="text-gray-600 text-xs">Urgency Signals</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-6">
                    {/* Top Companies */}
                    <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                        <h3 className="font-semibold text-white mb-4">Top Companies by Volume</h3>
                        <div className="space-y-3">
                            {(data?.top_companies || []).slice(0, 8).map((c, i) => (
                                <div key={i} className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
                                    <div className="flex items-center gap-3">
                                        <span className="text-gray-500 text-sm w-5">{i + 1}</span>
                                        <span className="text-white">{c.company}</span>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <span className="text-gray-400 text-sm">{c.count} contacts</span>
                                        <span className="text-green-400 font-medium">{c.avg_score?.toFixed(0) || '-'}</span>
                                    </div>
                                </div>
                            ))}
                            {(!data?.top_companies || data.top_companies.length === 0) && (
                                <p className="text-gray-500 text-center py-4">No company data yet</p>
                            )}
                        </div>
                    </div>

                    {/* Cold Call Funnel */}
                    <div className="bg-[#1e2228] rounded-xl border border-gray-800 p-5">
                        <h3 className="font-semibold text-white mb-4">Cold Call Funnel</h3>
                        <div className="space-y-4">
                            {[
                                { label: 'In Queue', value: data?.cold_call_stats?.total || 0, color: 'bg-gray-600' },
                                { label: 'New', value: data?.cold_call_stats?.new || 0, color: 'bg-blue-500' },
                                { label: 'Attempted', value: data?.cold_call_stats?.attempted || 0, color: 'bg-yellow-500' },
                                { label: 'Connected', value: data?.cold_call_stats?.connected || 0, color: 'bg-green-500' },
                                { label: 'Meetings Set', value: data?.cold_call_stats?.meeting_set || 0, color: 'bg-purple-500' },
                            ].map((stage, i) => (
                                <div key={i} className="flex items-center gap-3">
                                    <span className="w-24 text-sm text-gray-400">{stage.label}</span>
                                    <div className="flex-1 h-6 bg-gray-800 rounded overflow-hidden">
                                        <div 
                                            className={`h-full ${stage.color} transition-all`}
                                            style={{ width: `${Math.max((stage.value / Math.max(data?.cold_call_stats?.total || 1, 1)) * 100, 3)}%` }}
                                        />
                                    </div>
                                    <span className="w-12 text-right text-white font-medium">{stage.value}</span>
                                </div>
                            ))}
                        </div>
                        {data?.cold_call_stats?.conversion_rate !== undefined && (
                            <div className="mt-4 pt-4 border-t border-gray-700 text-center">
                                <p className="text-gray-400 text-sm">Meeting Conversion Rate</p>
                                <p className="text-2xl font-bold text-purple-400">
                                    {data.cold_call_stats.conversion_rate.toFixed(1)}%
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
