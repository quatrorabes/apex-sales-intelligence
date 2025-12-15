import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
    Zap, Users, Target, TrendingUp, Phone, Mail, BarChart3,
    Sparkles, ChevronRight, Brain, Shield, Rocket, Star,
    ArrowRight, Check, Play, Clock, Building2
} from 'lucide-react';

const API_URL = 'https://apex-backend-i7b0.onrender.com';

interface QuickStats {
    total_contacts: number;
    enriched: number;
    high_priority: number;
    cold_queue: number;
}

export default function LandingPage() {
    const [stats, setStats] = useState<QuickStats | null>(null);
    const [userName, setUserName] = useState<string>('');

    useEffect(() => {
        fetchStats();
        fetchUser();
    }, []);

    const fetchStats = async () => {
        try {
            const res = await fetch(`${API_URL}/api/todays-board`);
            const data = await res.json();
            setStats({
                total_contacts: data.stats?.total_contacts || 0,
                enriched: data.stats?.enriched || 0,
                high_priority: data.stats?.high_match || 0,
                cold_queue: data.stats?.cold_call_queue || 0,
            });
        } catch (e) {
            console.error(e);
        }
    };

    const fetchUser = async () => {
        try {
            const res = await fetch(`${API_URL}/api/user/profile?user_id=default`);
            const data = await res.json();
            if (data.full_name) {
                setUserName(data.full_name.split(' ')[0]);
            }
        } catch (e) {}
    };

    const getGreeting = () => {
        const hour = new Date().getHours();
        if (hour < 12) return 'Good morning';
        if (hour < 17) return 'Good afternoon';
        return 'Good evening';
    };

    const QuickAction = ({ 
        to, icon, title, subtitle, color, count 
    }: { 
        to: string; 
        icon: React.ReactNode; 
        title: string; 
        subtitle: string;
        color: string;
        count?: number;
    }) => (
        <Link
            to={to}
            className="group bg-[#1e2228] hover:bg-[#252a31] border border-gray-800 hover:border-gray-700 rounded-xl p-5 transition-all"
        >
            <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-xl ${color}`}>
                    {icon}
                </div>
                {count !== undefined && (
                    <span className="text-2xl font-bold text-white">{count}</span>
                )}
            </div>
            <h3 className="font-semibold text-white mb-1 flex items-center gap-2">
                {title}
                <ChevronRight size={16} className="text-gray-600 group-hover:text-white group-hover:translate-x-1 transition-all" />
            </h3>
            <p className="text-gray-500 text-sm">{subtitle}</p>
        </Link>
    );

    return (
        <div className="min-h-screen bg-[#0f1114] text-white">
            {/* Hero Section */}
            <div className="relative overflow-hidden">
                {/* Background gradient */}
                <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-transparent to-blue-900/20" />
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-purple-500/10 rounded-full blur-3xl" />
                
                <div className="relative px-6 py-12 max-w-6xl mx-auto">
                    {/* Nav */}
                    <nav className="flex items-center justify-between mb-16">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
                                <Zap size={24} className="text-white" />
                            </div>
                            <span className="text-xl font-bold">APEX</span>
                            <span className="text-gray-500 text-sm">Sales Intelligence</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <Link to="/analytics" className="text-gray-400 hover:text-white transition">Analytics</Link>
                            <Link to="/contacts" className="text-gray-400 hover:text-white transition">Contacts</Link>
                            <Link 
                                to="/board" 
                                className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg font-medium transition"
                            >
                                Open Dashboard
                            </Link>
                        </div>
                    </nav>

                    {/* Hero Content */}
                    <div className="text-center mb-16">
                        <h1 className="text-5xl font-bold mb-4">
                            {getGreeting()}{userName ? `, ${userName}` : ''} 👋
                        </h1>
                        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                            Your AI-powered sales intelligence platform. Enrich contacts, score leads, 
                            and close deals faster.
                        </p>
                    </div>

                    {/* Quick Stats */}
                    <div className="grid grid-cols-4 gap-4 mb-16">
                        <div className="bg-[#1e2228]/80 backdrop-blur border border-gray-800 rounded-xl p-5 text-center">
                            <p className="text-4xl font-bold text-white">{stats?.total_contacts || 0}</p>
                            <p className="text-gray-500 text-sm">Total Contacts</p>
                        </div>
                        <div className="bg-[#1e2228]/80 backdrop-blur border border-gray-800 rounded-xl p-5 text-center">
                            <p className="text-4xl font-bold text-purple-400">{stats?.enriched || 0}</p>
                            <p className="text-gray-500 text-sm">Enriched</p>
                        </div>
                        <div className="bg-[#1e2228]/80 backdrop-blur border border-gray-800 rounded-xl p-5 text-center">
                            <p className="text-4xl font-bold text-green-400">{stats?.high_priority || 0}</p>
                            <p className="text-gray-500 text-sm">High Priority</p>
                        </div>
                        <div className="bg-[#1e2228]/80 backdrop-blur border border-gray-800 rounded-xl p-5 text-center">
                            <p className="text-4xl font-bold text-blue-400">{stats?.cold_queue || 0}</p>
                            <p className="text-gray-500 text-sm">In Call Queue</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Quick Actions Grid */}
            <div className="px-6 py-12 max-w-6xl mx-auto">
                <h2 className="text-2xl font-bold mb-6">Quick Actions</h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <QuickAction
                        to="/board"
                        icon={<Target size={24} />}
                        title="Today's Board"
                        subtitle="View prioritized leads for today"
                        color="bg-yellow-500/20 text-yellow-400"
                        count={stats?.high_priority}
                    />
                    <QuickAction
                        to="/contacts"
                        icon={<Users size={24} />}
                        title="All Contacts"
                        subtitle="Browse and manage your pipeline"
                        color="bg-blue-500/20 text-blue-400"
                        count={stats?.total_contacts}
                    />
                    <QuickAction
                        to="/cold-call"
                        icon={<Phone size={24} />}
                        title="Cold Call Queue"
                        subtitle="Work through your call list"
                        color="bg-purple-500/20 text-purple-400"
                        count={stats?.cold_queue}
                    />
                    <QuickAction
                        to="/smart-lists"
                        icon={<Sparkles size={24} />}
                        title="Smart Lists"
                        subtitle="Auto-segmented lead lists"
                        color="bg-cyan-500/20 text-cyan-400"
                    />
                    <QuickAction
                        to="/analytics"
                        icon={<BarChart3 size={24} />}
                        title="Analytics"
                        subtitle="Pipeline metrics and insights"
                        color="bg-green-500/20 text-green-400"
                    />
                    <Link
                        to="/contacts?view=kanban"
                        className="group bg-gradient-to-br from-purple-900/50 to-blue-900/50 hover:from-purple-900/70 hover:to-blue-900/70 border border-purple-500/30 rounded-xl p-5 transition-all"
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div className="p-3 rounded-xl bg-purple-500/20 text-purple-400">
                                <Rocket size={24} />
                            </div>
                        </div>
                        <h3 className="font-semibold text-white mb-1 flex items-center gap-2">
                            Kanban View
                            <ArrowRight size={16} className="text-purple-400 group-hover:translate-x-1 transition-all" />
                        </h3>
                        <p className="text-gray-400 text-sm">Visual pipeline management</p>
                    </Link>
                </div>
            </div>

            {/* Features Section */}
            <div className="px-6 py-12 max-w-6xl mx-auto border-t border-gray-800">
                <h2 className="text-2xl font-bold mb-8 text-center">Powered by AI</h2>
                <div className="grid md:grid-cols-3 gap-6">
                    <div className="text-center">
                        <div className="w-14 h-14 bg-purple-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                            <Brain size={28} className="text-purple-400" />
                        </div>
                        <h3 className="font-semibold text-white mb-2">Smart Enrichment</h3>
                        <p className="text-gray-500 text-sm">
                            AI researches each contact, building comprehensive profiles from public data
                        </p>
                    </div>
                    <div className="text-center">
                        <div className="w-14 h-14 bg-green-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                            <Target size={28} className="text-green-400" />
                        </div>
                        <h3 className="font-semibold text-white mb-2">Match Scoring</h3>
                        <p className="text-gray-500 text-sm">
                            Personalized scoring based on YOUR ideal client profile and products
                        </p>
                    </div>
                    <div className="text-center">
                        <div className="w-14 h-14 bg-blue-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                            <Mail size={28} className="text-blue-400" />
                        </div>
                        <h3 className="font-semibold text-white mb-2">AI Outreach</h3>
                        <p className="text-gray-500 text-sm">
                            Generate personalized emails and LinkedIn messages in one click
                        </p>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-8 border-t border-gray-800">
                <div className="max-w-6xl mx-auto flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center gap-2">
                        <Zap size={16} className="text-purple-400" />
                        <span>APEX Sales Intelligence v4.0</span>
                    </div>
                    <div>
                        Built for closers 🎯
                    </div>
                </div>
            </div>
        </div>
    );
}
