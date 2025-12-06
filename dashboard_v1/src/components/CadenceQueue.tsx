// =============================================================================
// CadenceQueue.tsx - Daily Action Queue for Cadence Management
// =============================================================================

import { useState, useEffect } from 'react';
import {
  Mail, Phone, Linkedin, Play, Check, Pause, SkipForward,
  Clock, Users, Target, ChevronRight, Loader2, RefreshCw,
  Calendar, Zap, MessageSquare, AlertCircle, CheckCircle2,
  ArrowRight, Filter
} from 'lucide-react';

interface QueueItem {
  enrollment_id: number;
  contact_id: number;
  contact_display: string;
  company: string;
  title: string;
  email: string;
  phone: string;
  match_score: number;
  match_tier: string;
  cadence_name: string;
  current_step: number;
  total_steps: number;
  progress: string;
  next_action_date: string;
  current_action: {
    channel: string;
    template: string;
    title: string;
    day: number;
  };
}

interface QueueStats {
  total: number;
  emails: number;
  calls: number;
  linkedin: number;
}

interface CadenceStats {
  total_enrollments: number;
  active: number;
  completed: number;
  replied: number;
  booked: number;
  reply_rate: number;
  activities_today: number;
  due_today: number;
}

const CHANNEL_CONFIG = {
  email: { icon: Mail, color: 'indigo', label: 'Email' },
  call: { icon: Phone, color: 'emerald', label: 'Call' },
  linkedin: { icon: Linkedin, color: 'blue', label: 'LinkedIn' }
};

export default function CadenceQueue({ onSelectContact }: { onSelectContact?: (id: number) => void }) {
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [stats, setStats] = useState<QueueStats>({ total: 0, emails: 0, calls: 0, linkedin: 0 });
  const [cadenceStats, setCadenceStats] = useState<CadenceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [processingId, setProcessingId] = useState<number | null>(null);

  useEffect(() => {
    fetchQueue();
    fetchStats();
  }, []);

  const fetchQueue = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/cadence-queue');
      const data = await res.json();
      setQueue(data.queue || []);
      setStats(data.summary || { total: 0, emails: 0, calls: 0, linkedin: 0 });
    } catch (e) {
      console.error('Failed to fetch queue:', e);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/cadence-stats');
      const data = await res.json();
      setCadenceStats(data);
    } catch (e) {
      console.error('Failed to fetch stats:', e);
    }
  };

  const handleComplete = async (item: QueueItem, outcome: string) => {
    setProcessingId(item.enrollment_id);
    try {
      await fetch(`http://localhost:8000/api/enrollments/${item.enrollment_id}/advance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'completed', outcome })
      });
      await fetchQueue();
      await fetchStats();
    } catch (e) {
      console.error('Failed to advance:', e);
    } finally {
      setProcessingId(null);
    }
  };

  const handleSkip = async (item: QueueItem) => {
    setProcessingId(item.enrollment_id);
    try {
      await fetch(`http://localhost:8000/api/enrollments/${item.enrollment_id}/advance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'skipped' })
      });
      await fetchQueue();
    } catch (e) {
      console.error('Failed to skip:', e);
    } finally {
      setProcessingId(null);
    }
  };

  const handlePause = async (item: QueueItem) => {
    setProcessingId(item.enrollment_id);
    try {
      await fetch(`http://localhost:8000/api/enrollments/${item.enrollment_id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'paused' })
      });
      await fetchQueue();
      await fetchStats();
    } catch (e) {
      console.error('Failed to pause:', e);
    } finally {
      setProcessingId(null);
    }
  };

  const filteredQueue = filter === 'all' ? queue : queue.filter(q => q.current_action.channel === filter);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-indigo-500" size={32} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Header */}
      {cadenceStats && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                <Target size={20} className="text-indigo-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{cadenceStats.active}</p>
                <p className="text-xs text-[#8b919a]">Active Sequences</p>
              </div>
            </div>
          </div>
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
                <Clock size={20} className="text-orange-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{cadenceStats.due_today}</p>
                <p className="text-xs text-[#8b919a]">Due Today</p>
              </div>
            </div>
          </div>
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                <CheckCircle2 size={20} className="text-emerald-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{cadenceStats.activities_today}</p>
                <p className="text-xs text-[#8b919a]">Completed Today</p>
              </div>
            </div>
          </div>
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <Zap size={20} className="text-purple-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{cadenceStats.reply_rate}%</p>
                <p className="text-xs text-[#8b919a]">Reply Rate</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-all ${
              filter === 'all' 
                ? 'bg-white/10 text-white' 
                : 'text-[#8b919a] hover:text-white'
            }`}
          >
            <Users size={16} />
            All ({stats.total})
          </button>
          <button
            onClick={() => setFilter('email')}
            className={`px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-all ${
              filter === 'email' 
                ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/50' 
                : 'text-[#8b919a] hover:text-white'
            }`}
          >
            <Mail size={16} />
            Emails ({stats.emails})
          </button>
          <button
            onClick={() => setFilter('call')}
            className={`px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-all ${
              filter === 'call' 
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/50' 
                : 'text-[#8b919a] hover:text-white'
            }`}
          >
            <Phone size={16} />
            Calls ({stats.calls})
          </button>
          <button
            onClick={() => setFilter('linkedin')}
            className={`px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-all ${
              filter === 'linkedin' 
                ? 'bg-blue-500/20 text-blue-300 border border-blue-500/50' 
                : 'text-[#8b919a] hover:text-white'
            }`}
          >
            <Linkedin size={16} />
            LinkedIn ({stats.linkedin})
          </button>
        </div>
        <button
          onClick={() => { setLoading(true); fetchQueue(); fetchStats(); }}
          className="p-2 text-[#8b919a] hover:text-white rounded-lg hover:bg-[#21262d]"
        >
          <RefreshCw size={18} />
        </button>
      </div>

      {/* Queue List */}
      {filteredQueue.length === 0 ? (
        <div className="text-center py-12 bg-[#161b22] border border-[#30363d] rounded-xl">
          <CheckCircle2 size={48} className="mx-auto text-emerald-500 mb-4" />
          <p className="text-white font-medium text-lg">All caught up!</p>
          <p className="text-[#8b919a] mt-1">No actions due right now.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredQueue.map((item) => {
            const channelConfig = CHANNEL_CONFIG[item.current_action.channel as keyof typeof CHANNEL_CONFIG];
            const Icon = channelConfig?.icon || Mail;
            const isProcessing = processingId === item.enrollment_id;
            
            return (
              <div
                key={item.enrollment_id}
                className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 hover:border-[#484f58] transition-all"
              >
                <div className="flex items-center gap-4">
                  {/* Channel Icon */}
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center bg-${channelConfig?.color}-500/20`}>
                    <Icon size={24} className={`text-${channelConfig?.color}-400`} />
                  </div>
                  
                  {/* Contact Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => onSelectContact?.(item.contact_id)}
                        className="font-medium text-white hover:text-indigo-400 truncate"
                      >
                        {item.contact_display}
                      </button>
                      {item.match_tier === 'HIGH' && (
                        <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">
                          Hot
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-[#8b919a] truncate">
                      {item.title} at {item.company}
                    </p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-[#6e7681]">
                      <span>{item.cadence_name}</span>
                      <span>•</span>
                      <span>Step {item.progress}</span>
                    </div>
                  </div>
                  
                  {/* Current Action */}
                  <div className="text-right">
                    <p className="text-sm font-medium text-white">{item.current_action.title}</p>
                    <p className="text-xs text-[#8b919a]">Day {item.current_action.day}</p>
                  </div>
                  
                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onSelectContact?.(item.contact_id)}
                      className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-lg text-sm font-medium flex items-center gap-2"
                    >
                      <Play size={14} />
                      Execute
                    </button>
                    <button
                      onClick={() => handleComplete(item, 'neutral')}
                      disabled={isProcessing}
                      className="p-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg disabled:opacity-50"
                      title="Mark Complete"
                    >
                      {isProcessing ? <Loader2 size={16} className="animate-spin" /> : <Check size={16} />}
                    </button>
                    <button
                      onClick={() => handleSkip(item)}
                      disabled={isProcessing}
                      className="p-2 bg-[#21262d] hover:bg-[#30363d] rounded-lg text-[#8b919a] hover:text-white disabled:opacity-50"
                      title="Skip Step"
                    >
                      <SkipForward size={16} />
                    </button>
                    <button
                      onClick={() => handlePause(item)}
                      disabled={isProcessing}
                      className="p-2 bg-[#21262d] hover:bg-[#30363d] rounded-lg text-[#8b919a] hover:text-white disabled:opacity-50"
                      title="Pause Cadence"
                    >
                      <Pause size={16} />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
