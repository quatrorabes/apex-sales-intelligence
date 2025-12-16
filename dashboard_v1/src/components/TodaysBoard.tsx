import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || "https://apex-backend-i7b0.onrender.com";

interface Contact {
  id: string;
  firstname?: string;
  lastname?: string;
  email?: string;
  company?: string;
  title?: string;
  apex_score?: number;
  unified_qualification_score?: number;
  enrichment_status?: string;
  match_tier?: string;
}

interface DashboardStats {
  total_contacts: number;
  enriched: number;
  high_match: number;
  medium_match: number;
  low_match: number;
  cold_call_queue: number;
}

interface BoardData {
  success: boolean;
  date: string;
  time: string;
  stats: DashboardStats;
  segments: {
    high: Contact[];
    medium: Contact[];
    low: Contact[];
  };
  top_priority: Contact[];
}

export default function TodaysBoard() {
  const navigate = useNavigate();
  const [data, setData] = useState<BoardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function fetchBoardData() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/todays-board`);
      if (!res.ok) throw new Error('Failed to fetch dashboard');
      const json = await res.json();
      setData(json);
    } catch (err: any) {
      console.error('Dashboard fetch error:', err);
      setError(err.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchBoardData();
    const interval = setInterval(fetchBoardData, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mx-auto mb-6"></div>
          <p className="text-slate-700 text-xl font-semibold">Loading Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-4">
        <div className="bg-white rounded-xl shadow-2xl p-8 max-w-lg w-full">
          <h2 className="text-2xl font-bold text-red-600 mb-4">⚠️ Dashboard Error</h2>
          <p className="text-slate-700 mb-6">{error || 'Unable to load dashboard data'}</p>
          <button 
            onClick={fetchBoardData} 
            className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg hover:bg-indigo-700 font-semibold transition"
          >
            🔄 Retry
          </button>
        </div>
      </div>
    );
  }

  const { stats, segments, top_priority } = data;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">📊 Today's Board</h1>
          <p className="text-xl text-slate-600">{data.date} • {data.time}</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-8">
          {[
            { label: 'Total Contacts', value: stats.total_contacts, icon: '👥', color: 'blue' },
            { label: 'Enriched', value: stats.enriched, icon: '✅', color: 'emerald' },
            { label: 'High Match', value: stats.high_match, icon: '⚡', color: 'purple' },
            { label: 'Medium Match', value: stats.medium_match, icon: '🎯', color: 'indigo' },
            { label: 'Low Match', value: stats.low_match, icon: '📊', color: 'slate' },
            { label: 'Call Queue', value: stats.cold_call_queue, icon: '☎️', color: 'amber' },
          ].map((stat) => (
            <div key={stat.label} className={`bg-white rounded-xl shadow-lg p-6 border-2 border-${stat.color}-100 hover:shadow-xl transition-all transform hover:-translate-y-1`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-3xl">{stat.icon}</span>
                <span className={`text-4xl font-bold text-${stat.color}-600`}>{stat.value}</span>
              </div>
              <p className="text-sm font-semibold text-slate-600">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Top Priority Contacts */}
        <div className="bg-white rounded-xl shadow-2xl mb-8 overflow-hidden border-2 border-purple-200">
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 px-8 py-6">
            <h2 className="text-2xl font-bold text-white flex items-center gap-3">
              <span>🔥</span>
              Top Priority Contacts
              <span className="ml-auto bg-white/20 px-4 py-1 rounded-full text-sm">
                {top_priority.length} Active
              </span>
            </h2>
          </div>
          <div className="p-6">
            {top_priority.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-slate-500 text-xl">No high-priority contacts yet.</p>
                <p className="text-slate-400 mt-2">Enrich contacts to populate this board.</p>
              </div>
            ) : (
              <div className="grid gap-4">
                {top_priority.map((contact) => (
                  <div
                    key={contact.id}
                    onClick={() => navigate(`/contacts/${contact.id}`)}
                    className="flex items-center justify-between p-6 bg-gradient-to-r from-slate-50 to-indigo-50 rounded-xl border-2 border-slate-200 hover:border-indigo-400 cursor-pointer transition-all transform hover:scale-105 hover:shadow-lg"
                  >
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900">
                        {contact.firstname} {contact.lastname}
                      </h3>
                      <p className="text-lg text-slate-700 font-semibold">{contact.title}</p>
                      <p className="text-md text-slate-600">{contact.company}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      {contact.apex_score && contact.apex_score > 0 && (
                        <div className="text-center">
                          <div className="text-3xl font-bold text-purple-600">
                            {contact.apex_score}
                          </div>
                          <div className="text-xs text-slate-500 font-semibold">APEX</div>
                        </div>
                      )}
                      <span className={`px-4 py-2 rounded-full text-sm font-bold ${
                        contact.enrichment_status === 'enriched' 
                          ? 'bg-emerald-100 text-emerald-800 border-2 border-emerald-300' 
                          : 'bg-amber-100 text-amber-800 border-2 border-amber-300'
                      }`}>
                        {contact.enrichment_status || 'pending'}
                      </span>
                      <button className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-semibold transition">
                        View →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Segmented Pipeline */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {[
            { key: 'high', title: '🔥 High Priority', contacts: segments.high, color: 'purple' },
            { key: 'medium', title: '🎯 Medium Priority', contacts: segments.medium, color: 'indigo' },
            { key: 'low', title: '📊 Low Priority', contacts: segments.low, color: 'slate' },
          ].map((segment) => (
            <div key={segment.key} className={`bg-white rounded-xl shadow-xl overflow-hidden border-2 border-${segment.color}-200`}>
              <div className={`bg-gradient-to-r from-${segment.color}-500 to-${segment.color}-600 px-6 py-4`}>
                <h3 className="text-xl font-bold text-white flex items-center justify-between">
                  {segment.title}
                  <span className="bg-white/20 px-3 py-1 rounded-full text-sm">
                    {segment.contacts.length}
                  </span>
                </h3>
              </div>
              <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
                {segment.contacts.length === 0 ? (
                  <p className="text-center text-slate-400 py-8">No contacts in this segment</p>
                ) : (
                  segment.contacts.map((contact) => (
                    <div
                      key={contact.id}
                      onClick={() => navigate(`/contacts/${contact.id}`)}
                      className="p-4 bg-slate-50 rounded-lg hover:bg-indigo-50 border border-slate-200 hover:border-indigo-300 cursor-pointer transition"
                    >
                      <p className="font-bold text-gray-900">
                        {contact.firstname} {contact.lastname}
                      </p>
                      <p className="text-sm text-slate-600">{contact.company}</p>
                      {contact.apex_score && contact.apex_score > 0 && (
                        <p className="text-xs text-purple-600 font-semibold mt-1">
                          APEX: {contact.apex_score}
                        </p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="mt-8 flex gap-4 justify-center">
          <button
            onClick={() => navigate('/contacts')}
            className="px-8 py-4 bg-indigo-600 text-white rounded-xl shadow-xl hover:bg-indigo-700 font-bold text-lg transition-all transform hover:scale-105"
          >
            👥 View All Contacts
          </button>
          <button
            onClick={fetchBoardData}
            className="px-8 py-4 bg-slate-200 text-slate-700 rounded-xl shadow-lg hover:bg-slate-300 font-semibold text-lg transition"
          >
            🔄 Refresh Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}
