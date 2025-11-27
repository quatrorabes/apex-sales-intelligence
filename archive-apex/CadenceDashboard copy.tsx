import React, { useEffect, useState } from "react";
import {
  Zap,
  Clock,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
} from "lucide-react";

type CadenceSequenceContact = {
  id: number;
  name: string;
  email: string | null;
  company: string | null;
  tier: string | null;
};

type CadenceSequence = {
  id: number;
  cadence_type: string;
  current_step: number;
  total_steps: number;
  started_at: string | null;
  next_touch_at: string | null;
  contact: CadenceSequenceContact;
};

type ActiveCadenceResponse = {
  sequences: CadenceSequence[];
  count: number;
};

type Summary = {
  active_cadences: number;
  completed_cadences: number;
  todays_activities: number;
  overdue_activities: number;
};

const API_BASE = "http://localhost:8000";

export default function CadenceDashboard() {
  const [summary, setSummary] = useState<Summary>({
    active_cadences: 0,
    completed_cadences: 0,
    todays_activities: 0,
    overdue_activities: 0,
  });
  const [sequences, setSequences] = useState<CadenceSequence[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCadenceData();
  }, []);

  const loadCadenceData = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/cadences/active`);
      if (!res.ok) {
        throw new Error(`API returned ${res.status}`);
      }
      const data: ActiveCadenceResponse = await res.json();
      const list = data.sequences || [];

      const now = new Date();
      const todayStr = now.toISOString().slice(0, 10);

      let todays = 0;
      let overdue = 0;

      list.forEach((s) => {
        if (!s.next_touch_at) return;
        const d = new Date(s.next_touch_at);
        const dateStr = d.toISOString().slice(0, 10);
        if (dateStr === todayStr) todays += 1;
        if (d.getTime() < now.getTime()) overdue += 1;
      });

      setSequences(list);
      setSummary({
        active_cadences: list.length,
        completed_cadences: 0, // /api/cadences/active only returns active ones
        todays_activities: todays,
        overdue_activities: overdue,
      });
    } catch (err: any) {
      console.error("Error loading cadence data:", err);
      setError(
        err?.message ||
          "Error loading cadences. Backend cadence APIs may not be wired yet."
      );
      setSequences([]);
      setSummary({
        active_cadences: 0,
        completed_cadences: 0,
        todays_activities: 0,
        overdue_activities: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (seq: CadenceSequence) => {
    const next = seq.next_touch_at ? new Date(seq.next_touch_at) : null;
    const now = new Date();

    if (!next) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-slate-800 text-slate-200">
          <Clock className="w-3 h-3" />
          Scheduled
        </span>
      );
    }

    if (next.getTime() < now.getTime()) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-red-900/50 text-red-300">
          <AlertCircle className="w-3 h-3" />
          Overdue
        </span>
      );
    }

    const todayStr = now.toISOString().slice(0, 10);
    const dateStr = next.toISOString().slice(0, 10);
    if (todayStr === dateStr) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-sky-900/50 text-sky-300">
          <Clock className="w-3 h-3" />
          Due Today
        </span>
      );
    }

    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs bg-emerald-900/40 text-emerald-300">
        <Clock className="w-3 h-3" />
        Upcoming
      </span>
    );
  };

  const formatDateTime = (value: string | null) => {
    if (!value) return "—";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return value;
    return d.toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-white">
            Cadence Control Center
          </h1>
          <p className="text-slate-400 mt-1 text-sm">
            See every touchpoint scheduled, what is overdue, and which
            cadences are driving your pipeline.
          </p>
        </div>
        <button
          onClick={loadCadenceData}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-100 rounded-lg text-sm font-medium disabled:opacity-50"
        >
          <RefreshCw
            className={`w-4 h-4 ${loading ? "animate-spin" : ""}`}
          />
          Refresh
        </button>
      </div>

      {/* Error banner only if the API call itself fails */}
      {error && (
        <div className="bg-amber-900/40 border border-amber-500/60 text-amber-100 px-4 py-3 rounded-lg text-sm">
          <p className="font-semibold mb-1">Cadence API Notice</p>
          <p>{error}</p>
          <p className="mt-1 text-xs text-amber-200">
            Once the cadence engine is wired to the database, this view will
            populate with active sequences and scheduled activities.
          </p>
        </div>
      )}

      {/* Metric cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400">
              Active Cadences
            </span>
            <Zap className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold text-white">
            {summary.active_cadences}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Contacts currently on automated sequences.
          </div>
        </div>
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400">
              Completed Cadences
            </span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold text-white">
            {summary.completed_cadences}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Sequences that have fully run to completion.
          </div>
        </div>
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400">
              Today&apos;s Tasks
            </span>
            <Clock className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-3xl font-bold text-white">
            {summary.todays_activities}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Emails, calls, and LinkedIn steps due today.
          </div>
        </div>
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400">
              Overdue Steps
            </span>
            <AlertCircle className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-3xl font-bold text-white">
            {summary.overdue_activities}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Tasks that slipped past their due date.
          </div>
        </div>
      </div>

      {/* Active sequences table */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">
            Active Cadence Sequences
          </h2>
          <span className="text-xs text-slate-400">
            Pulled from /api/cadences/active
          </span>
        </div>
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-6 text-center text-slate-400 text-sm">
              Loading cadence sequences…
            </div>
          ) : sequences.length === 0 ? (
            <div className="p-6 text-center text-slate-400 text-sm">
              No active cadence sequences found yet. Start cadences for
              contacts from your backend tools to see them here.
            </div>
          ) : (
            <table className="min-w-full text-sm">
              <thead className="bg-slate-900 border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Contact
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Cadence
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Progress
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Next Touch
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {sequences.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-800/60">
                    <td className="px-4 py-3">
                      <div className="font-semibold text-white">
                        {s.contact?.name}
                      </div>
                      <div className="text-xs text-slate-400">
                        {s.contact?.company || "—"}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-200">
                      {s.cadence_type}
                    </td>
                    <td className="px-4 py-3 text-slate-200">
                      Step {s.current_step} of {s.total_steps}
                    </td>
                    <td className="px-4 py-3 text-slate-200">
                      {formatDateTime(s.next_touch_at)}
                    </td>
                    <td className="px-4 py-3">{getStatusBadge(s)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
