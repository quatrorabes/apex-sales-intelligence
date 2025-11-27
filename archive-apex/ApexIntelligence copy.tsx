import React, { useEffect, useState } from "react";

type ApexContact = {
  id: number;
  name: string;
  company: string | null;
  email: string | null;
  title: string | null;
  lead_type: string | null;
  lifecycle_stage: string | null;
  mdcp_score: number | null;  // Changed from mdcp_total
  mdcp_tier: string | null;
  rss_score: number | null;   // Changed from rss_total
  rss_tier: string | null;
  priority_score: number | null;
  urgency_level: string | null;
  recommended_action: string | null;
};

type ApexApiResponse = {
  status: string;
  count: number;
  contacts: ApexContact[];
};

export function ApexIntelligenceDashboard({ contacts: propContacts }: { contacts?: any[] }) {
  const [contacts, setContacts] = useState<ApexContact[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState<boolean>(false);

  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    // If contacts passed as props, use those
    if (propContacts && propContacts.length > 0) {
      const scoredContacts = propContacts.filter(c => c.priority_score !== null && c.priority_score !== undefined);
      setContacts(scoredContacts);
      setLoading(false);
    } else {
      fetchApexScores();
    }
  }, [propContacts]);

  const fetchApexScores = async () => {
    setLoading(true);
    setError(null);

    try {
      // Try the apex endpoint first
      let res = await fetch(`${API_BASE}/api/apex/scores`);
      
      // If apex endpoint doesn't exist, try regular contacts endpoint
      if (!res.ok) {
        res = await fetch(`${API_BASE}/api/contacts`);
        if (!res.ok) {
          throw new Error(`API returned ${res.status}`);
        }
        const allContacts = await res.json();
        // Filter for scored contacts only
        const scoredContacts = allContacts.filter((c: any) => c.priority_score !== null && c.priority_score !== undefined);
        setContacts(scoredContacts);
      } else {
        const data: ApexApiResponse = await res.json();
        setContacts(data.contacts || []);
      }
    } catch (err: any) {
      console.error("Error fetching scores:", err);
      setError("Error loading scores. Check if API is running.");
    } finally {
      setLoading(false);
    }
  };

  const runScoring = async () => {
    setRunning(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/contacts/score-batch`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ limit: 50 })
      });
      
      if (!res.ok) {
        throw new Error(`Score API returned ${res.status}`);
      }
      
      const result = await res.json();
      if (result.success) {
        // Give backend a moment then reload scores
        setTimeout(fetchApexScores, 1500);
      }
    } catch (err: any) {
      console.error("Error running scoring:", err);
      setError("Error running scoring. Check backend logs.");
    } finally {
      setRunning(false);
    }
  };

  const getUrgencyColor = (urgency?: string | null) => {
    const level = (urgency || "").toUpperCase();
    switch (level) {
      case "IMMEDIATE":
        return "bg-red-500 text-white";
      case "HIGH":
        return "bg-orange-500 text-white";
      case "MEDIUM":
        return "bg-yellow-400 text-slate-900";
      case "LOW":
        return "bg-gray-500 text-white";
      default:
        return "bg-slate-600 text-slate-100";
    }
  };

  const getTierColor = (tier?: string | null) => {
    switch ((tier || "").toUpperCase()) {
      case "HOT":
        return "bg-red-600 text-white";
      case "WARM":
        return "bg-orange-500 text-white";
      case "QUALIFIED":
        return "bg-blue-600 text-white";
      case "COLD":
        return "bg-slate-600 text-white";
      default:
        return "bg-slate-700 text-slate-100";
    }
  };

  const getLifecycleColor = (stage?: string | null) => {
    switch ((stage || "").toUpperCase()) {
      case "NEW":
        return "text-green-400";
      case "WARMING":
        return "text-yellow-400";
      case "ACTIVE":
        return "text-blue-400";
      case "ESTABLISHED":
        return "text-purple-400";
      default:
        return "text-slate-400";
    }
  };

  const immediateCount = contacts.filter(c => c.urgency_level === "IMMEDIATE").length;
  const highCount = contacts.filter(c => c.urgency_level === "HIGH").length;
  const avgPriority = contacts.length === 0 ? 0 : Math.round(
    contacts.reduce((sum, c) => sum + (c.priority_score ?? 0), 0) / contacts.length
  );

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Apex Intelligence</h1>
          <p className="text-slate-400 mt-1">
            CRE-focused scoring with MDCP + RSS prioritization
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={fetchApexScores}
            disabled={loading || running}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-100 rounded-lg text-sm font-medium disabled:opacity-50"
          >
            Refresh
          </button>
          <button
            onClick={runScoring}
            disabled={running}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium disabled:opacity-50 flex items-center gap-2"
          >
            {running ? (
              <>
                <span className="w-3 h-3 rounded-full border-2 border-white border-t-transparent animate-spin" />
                Running…
              </>
            ) : (
              <>Run Scoring</>
            )}
          </button>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="bg-red-900/40 border border-red-500/60 text-red-100 px-4 py-3 rounded-lg text-sm">
          <p className="font-semibold mb-1">Error</p>
          <p>{error}</p>
        </div>
      )}

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-4">
          <div className="text-xs font-semibold text-slate-400 mb-1">
            🔥 Immediate Action
          </div>
          <div className="text-3xl font-bold text-white">{immediateCount}</div>
          <div className="text-xs text-slate-500 mt-1">
            Hot CRE leads - contact today
          </div>
        </div>
        <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-4">
          <div className="text-xs font-semibold text-slate-400 mb-1">
            ⚡ High Priority
          </div>
          <div className="text-3xl font-bold text-white">{highCount}</div>
          <div className="text-xs text-slate-500 mt-1">
            Strong prospects - this week
          </div>
        </div>
        <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-4">
          <div className="text-xs font-semibold text-slate-400 mb-1">
            📊 Average Score
          </div>
          <div className="text-3xl font-bold text-white">{avgPriority}</div>
          <div className="text-xs text-slate-500 mt-1">
            Mean priority across contacts
          </div>
        </div>
        <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-4">
          <div className="text-xs font-semibold text-slate-400 mb-1">
            ✅ Total Scored
          </div>
          <div className="text-3xl font-bold text-white">
            {contacts.length}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Contacts with Apex scores
          </div>
        </div>
      </div>

      {/* Contacts table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">
            Priority CRE Contacts
          </h2>
          <p className="text-xs text-slate-400">
            Sorted by priority (70% role, 30% data completeness)
          </p>
        </div>
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 text-center text-slate-400">Loading…</div>
          ) : contacts.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">
              No scored contacts yet. Click "Run Scoring" to analyze your contacts.
            </div>
          ) : (
            <table className="min-w-full text-sm">
              <thead className="bg-slate-900 border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Contact
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Title & Company
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-slate-400">
                    Lifecycle
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-slate-400">
                    MDCP
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-slate-400">
                    RSS
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-slate-400">
                    Priority
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-slate-400">
                    Urgency
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {contacts
                  .slice()
                  .sort((a, b) => (b.priority_score ?? 0) - (a.priority_score ?? 0))
                  .map((c) => (
                    <tr key={c.id} className="hover:bg-slate-800/60">
                      <td className="px-4 py-3">
                        <div className="font-semibold text-white">
                          {c.name}
                        </div>
                        <div className="text-xs text-slate-400">
                          {c.email || "No email"}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-slate-200 text-sm">
                          {c.title || "—"}
                        </div>
                        <div className="text-xs text-slate-400">
                          {c.company || "No company"}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`text-sm font-medium ${getLifecycleColor(c.lifecycle_stage)}`}>
                          {c.lifecycle_stage || "—"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className="text-sm font-medium text-slate-200">
                          {c.mdcp_score != null ? Math.round(c.mdcp_score) : "—"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className="text-sm font-medium text-slate-200">
                          {c.rss_score != null ? Math.round(c.rss_score) : "—"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="text-lg font-bold text-white">
                          {c.priority_score != null ? Math.round(c.priority_score) : "—"}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span
                          className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${getUrgencyColor(
                            c.urgency_level
                          )}`}
                        >
                          {c.urgency_level || "—"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-300 max-w-xs">
                        {c.recommended_action || "Score to get recommendation"}
                      </td>
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
