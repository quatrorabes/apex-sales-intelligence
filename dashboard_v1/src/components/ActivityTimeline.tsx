import { useState, useEffect } from 'react';
import { 
    Clock, Mail, Phone, Zap, Target, MessageSquare, 
    Calendar, CheckCircle, AlertCircle, User, TrendingUp,
    Linkedin, FileText, Star
} from 'lucide-react';

const API_URL = 'https://apex-backend-i7b0.onrender.com';

interface Activity {
    id: number;
    type: 'enrichment' | 'score' | 'email' | 'call' | 'meeting' | 'note' | 'linkedin' | 'status_change';
    title: string;
    description?: string;
    timestamp: string;
    metadata?: any;
}

const activityIcons: Record<string, { icon: React.ReactNode; color: string; bg: string }> = {
    enrichment: { icon: <Zap size={16} />, color: 'text-purple-400', bg: 'bg-purple-500/20' },
    score: { icon: <Target size={16} />, color: 'text-green-400', bg: 'bg-green-500/20' },
    email: { icon: <Mail size={16} />, color: 'text-blue-400', bg: 'bg-blue-500/20' },
    call: { icon: <Phone size={16} />, color: 'text-yellow-400', bg: 'bg-yellow-500/20' },
    meeting: { icon: <Calendar size={16} />, color: 'text-cyan-400', bg: 'bg-cyan-500/20' },
    note: { icon: <FileText size={16} />, color: 'text-gray-400', bg: 'bg-gray-500/20' },
    linkedin: { icon: <Linkedin size={16} />, color: 'text-blue-500', bg: 'bg-blue-600/20' },
    status_change: { icon: <TrendingUp size={16} />, color: 'text-orange-400', bg: 'bg-orange-500/20' },
};

export default function ActivityTimeline({ contactId }: { contactId: number }) {
    const [activities, setActivities] = useState<Activity[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchActivities();
    }, [contactId]);

    const fetchActivities = async () => {
        try {
            const res = await fetch(`${API_URL}/api/contacts/${contactId}/activities`);
            const data = await res.json();
            setActivities(data.activities || []);
        } catch (e) {
            console.error('Failed to fetch activities');
        } finally {
            setLoading(false);
        }
    };

    const formatTime = (timestamp: string) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const days = Math.floor(hours / 24);
        
        if (hours < 1) return 'Just now';
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        return date.toLocaleDateString();
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-8">
                <div className="w-6 h-6 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="space-y-1">
            {activities.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                    <Clock className="w-12 h-12 mx-auto mb-3 opacity-30" />
                    <p>No activity yet</p>
                </div>
            ) : (
                <div className="relative">
                    {/* Timeline line */}
                    <div className="absolute left-5 top-0 bottom-0 w-px bg-gray-800" />
                    
                    {activities.map((activity, i) => {
                        const { icon, color, bg } = activityIcons[activity.type] || activityIcons.note;
                        return (
                            <div key={activity.id || i} className="relative flex gap-4 pb-6 last:pb-0">
                                {/* Icon */}
                                <div className={`relative z-10 w-10 h-10 rounded-full ${bg} flex items-center justify-center ${color}`}>
                                    {icon}
                                </div>
                                
                                {/* Content */}
                                <div className="flex-1 pt-1">
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <p className="font-medium text-white">{activity.title}</p>
                                            {activity.description && (
                                                <p className="text-gray-400 text-sm mt-1">{activity.description}</p>
                                            )}
                                        </div>
                                        <span className="text-gray-500 text-sm whitespace-nowrap ml-4">
                                            {formatTime(activity.timestamp)}
                                        </span>
                                    </div>
                                    
                                    {/* Metadata */}
                                    {activity.metadata && (
                                        <div className="mt-2 p-3 bg-[#0f1114] rounded-lg border border-gray-800 text-sm">
                                            {activity.type === 'score' && activity.metadata.score && (
                                                <div className="flex items-center gap-4">
                                                    <span className="text-white">Score: <strong>{activity.metadata.score}</strong></span>
                                                    <span className="text-gray-500">Tier: {activity.metadata.tier}</span>
                                                </div>
                                            )}
                                            {activity.type === 'email' && activity.metadata.subject && (
                                                <p className="text-gray-400">Subject: {activity.metadata.subject}</p>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
