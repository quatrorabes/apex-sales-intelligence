import React, { useEffect, useState } from "react";

type ApexContact = {
  id: number;
  name: string;
  company: string | null;
  email: string | null;
  lead_type: string | null;
  lifecycle_stage: string | null;
  mdcp_total: number | null;
  mdcp_tier: string | null;
  rss_total: number | null;
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

export function ApexIntelligenceDashboard() {
  const [contacts, setContacts] = useState<ApexContact[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState<boolean>(false);

  const API_BASE = "http://localhost:8000";

  useEffect(() => {
    fetchApexScores();
  }, []);

  const fetchApexScores = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/apex/scores`);
      if (!res.ok) {
        throw new Error(`API returned ${res.status}`);
      }
      const data: ApexApiResponse = await res.json();
      setContacts(data.contacts || []);
    } catch (err: any) {
      console.error("Error fetching Apex scores:", err);
      if (err?.message?.includes("Failed to fetch")) {
        setError(
          "Cannot reach Apex Intelligence API at http://localhost:8000. Make sure the FastAPI server is running."
        );
      } else {
        setError(err?.message || "Unknown error loading Apex scores.");
      }
    } finally {
      setLoading(false);
    }
  };

  const runScoring = async () => {
    setRunning(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/apex/score-all`, {
        method: "POST",
      });
      if (!res.ok) {
        throw new Error(`Score-all API returned ${res.status}`);
      }
      // Give backend a moment then reload scores
      setTimeout(fetchApexScores, 1500);
    } catch (err: any) {
      console.error("Error running scoring:", err);
      setError(
        err?.message ||
          "Error running scoring. Check backend logs for more details."
      );
    } finally {
      setRunning(false);
    }
  };

  const getUrgencyColor = (urgency?: string | null) => {
    switch (urgency) {
      case "IMMEDIATE":
        return "bg-red-500 text-white";
      case "HIGH":
        return "bg-orange-500 text-white";
      case "MEDIUM":
        return "bg-yellow-400 text-slate-900";
      case "LOW":
        return "bg-emerald-500 text-white";
      default:
        return "bg-slate-600 text-slate-100";
    }
  };

  const getTierColor = (tier?: string | null) => {
    switch ((tier || "").toUpperCase()) {
      case "PLATINUM":
        return "bg-purple-600 text-white";
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

  const immediateCount = contacts.filter(
    (c) => c.urgency_level === "IMMEDIATE"
  ).length;
  const highCount = contacts.filter((c) => c.urgency_level === "HIGH").length;
  const avgPriority =
    contacts.length === 0
      ? 0
      : Math.round(
          contacts.reduce(
            (sum, c) => sum + (c.priority_score ?? 0),
            0
          ) / contacts.length
        );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Apex Intelligence</h1>
          <p className="text-slate-400 mt-1">
            MDCP + RSS scoring layered into a single prioritized action list.
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
          <p className="font-semibold mb-1">Apex API Error</p>
          <p>{error}</p>
          <p className="mt-1 text-xs text-red-200">
            Ensure the FastAPI backend is running on port 8000 and that the
            /api/apex/scores and /api/apex/score-all routes are available.
          </p>
        </div>
      )}

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-4">
          <div className="text-xs font-semibold text-slate-400 mb-1">
            Immediate Action
          </div>
          <div className="text-3xl font-bold text-white">{immediateCount}</div>
          <div className="text-xs text-slate-500 mt-1">
            Contacts requiring same‑day action.
          </div>
        </div>
        <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-4">
          <div className="text-xs font-semibold text-slate-400 mb-1">
            High Priority
          </div>
          <div className="text-3xl font-bold text-white">{highCount}</div>
          <div className="text-xs text-slate-500 mt-1">
            Strong deals worth scheduling this week.
          </div>
        </div>
        <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-4">
          <div className="text-xs font-semibold text-slate-400 mb-1">
            Average Priority
          </div>
          <div className="text-3xl font-bold text-white">{avgPriority}</div>
          <div className="text-xs text-slate-500 mt-1">
            Mean blended MDCP/RSS across scored contacts.
          </div>
        </div>
        <div className="bg-slate-900/60 border border-slate-700 rounded-xl p-4">
          <div className="text-xs font-semibold text-slate-400 mb-1">
            Total Scored
          </div>
          <div className="text-3xl font-bold text-white">
            {contacts.length}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Contacts with Apex Intelligence scores.
          </div>
        </div>
      </div>

      {/* Contacts table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">
            Priority Contacts
          </h2>
          <p className="text-xs text-slate-400">
            Sorted by blended priority score (MDCP × RSS).
          </p>
        </div>
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 text-center text-slate-400">Loading…</div>
          ) : contacts.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">
              No Apex Intelligence scores found yet. Enrich some contacts from
              the Contacts tab, then run scoring.
            </div>
          ) : (
            <table className="min-w-full text-sm">
              <thead className="bg-slate-900 border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Name
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Company
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Lifecycle
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    MDCP
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    RSS
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
                    Priority
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">
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
                  .sort(
                    (a, b) =>
                      (b.priority_score ?? 0) - (a.priority_score ?? 0)
                  )
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
                      <td className="px-4 py-3 text-slate-200">
                        {c.company || "—"}
                      </td>
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-full bg-slate-800 text-xs text-slate-200 border border-slate-700">
                          {c.lead_type || "UNKNOWN"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-200">
                        {c.lifecycle_stage || "—"}
                      </td>
                      <td className="px-4 py-3">
                        {c.mdcp_total != null ? (
                          <span
                            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTierColor(
                              c.mdcp_tier
                            )}`}
                          >
                            {c.mdcp_total.toFixed(0)}{" "}
                            {c.mdcp_tier ? `• ${c.mdcp_tier}` : ""}
                          </span>
                        ) : (
                          <span className="text-slate-500 text-xs">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {c.rss_total != null ? (
                          <span
                            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTierColor(
                              c.rss_tier
                            )}`}
                          >
                            {c.rss_total.toFixed(0)}{" "}
                            {c.rss_tier ? `• ${c.rss_tier}` : ""}
                          </span>
                        ) : (
                          <span className="text-slate-500 text-xs">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-white font-semibold">
                          {c.priority_score?.toFixed(0) ?? "—"}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getUrgencyColor(
                            c.urgency_level
                          )}`}
                        >
                          {c.urgency_level || "N/A"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-300 max-w-xs">
                        {c.recommended_action || "No recommendation."}
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
