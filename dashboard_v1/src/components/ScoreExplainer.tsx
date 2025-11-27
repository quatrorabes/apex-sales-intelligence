// ScoreExplainer.tsx - Interactive scoring breakdown
import React, { useState } from 'react';
import { Info, Target, Building2, User, TrendingUp } from 'lucide-react';

export function ScoreExplainer({ contact }: { contact: any }) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <>
      {/* Inline Score Badge with Info Icon */}
      <div className="inline-flex items-center gap-2">
        <span className="text-2xl font-bold text-white">{contact.priority_score}</span>
        <button
          onClick={() => setShowDetails(true)}
          className="p-1 rounded-full hover:bg-slate-700 transition-colors"
        >
          <Info className="w-4 h-4 text-slate-400 hover:text-blue-400" />
        </button>
      </div>

      {/* Score Breakdown Modal */}
      {showDetails && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl p-6 max-w-md w-full">
            <h3 className="text-xl font-bold text-white mb-4">How We Score {contact.name}</h3>
            
            <div className="space-y-4">
              {/* RSS Score - Role/Seniority */}
              <div className="bg-slate-900 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-blue-400" />
                    <span className="font-medium text-white">Role Fit (70%)</span>
                  </div>
                  <span className="text-xl font-bold text-blue-400">{contact.rss_score}</span>
                </div>
                <div className="text-sm text-slate-400">
                  {contact.title?.includes('VP') || contact.title?.includes('Director') 
                    ? "✅ Senior decision maker in CRE"
                    : contact.title?.includes('Manager')
                    ? "⚠️ Mid-level, may need approval"
                    : "❌ Not ideal seniority level"}
                </div>
                <div className="mt-2 bg-slate-800 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${contact.rss_score}%` }}
                  />
                </div>
              </div>

              {/* MDCP Score - Data Completeness */}
              <div className="bg-slate-900 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-green-400" />
                    <span className="font-medium text-white">Data Quality (30%)</span>
                  </div>
                  <span className="text-xl font-bold text-green-400">{contact.mdcp_score}</span>
                </div>
                <div className="text-sm text-slate-400">
                  <div className="flex flex-wrap gap-2 mt-2">
                    {contact.email && <span className="px-2 py-1 bg-green-900/30 text-green-400 rounded text-xs">✓ Email</span>}
                    {contact.phone && <span className="px-2 py-1 bg-green-900/30 text-green-400 rounded text-xs">✓ Phone</span>}
                    {contact.linkedin_url && <span className="px-2 py-1 bg-green-900/30 text-green-400 rounded text-xs">✓ LinkedIn</span>}
                    {contact.enriched && <span className="px-2 py-1 bg-blue-900/30 text-blue-400 rounded text-xs">✓ Enriched</span>}
                  </div>
                </div>
              </div>

              {/* Final Score */}
              <div className="bg-gradient-to-r from-blue-900/30 to-green-900/30 rounded-lg p-4 border border-slate-700">
                <div className="text-center">
                  <div className="text-3xl font-bold text-white">{contact.priority_score}</div>
                  <div className="text-sm text-slate-400 mt-1">Final Priority Score</div>
                  <div className="text-xs text-slate-500 mt-2">
                    (RSS × 0.7) + (MDCP × 0.3) = Priority
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={() => setShowDetails(false)}
              className="mt-6 w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Got it!
            </button>
          </div>
        </div>
      )}
    </>
  );
}
