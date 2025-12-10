import React, { useState, useEffect } from 'react';
import { Target, TrendingUp, Users, CheckCircle, AlertCircle } from 'lucide-react';

interface QualificationTabProps {
  contactId: number;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://apex-backend-i7b0.onrender.com';

export function QualificationTab({ contactId }: QualificationTabProps) {
  const [qualData, setQualData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchQualification();
  }, [contactId]);

  const fetchQualification = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/contacts/${contactId}/qualification-report?framework=HYBRID`
      );
      const data = await response.json();
      if (data.success) {
        setQualData(data);
      }
    } catch (error) {
      console.error('Failed to fetch qualification:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!qualData) {
    return (
      <div className="text-center py-12 text-gray-500">
        No qualification data available
      </div>
    );
  }

  const { unified_qualification, recommendation } = qualData;
  const { bant_breakdown, spice_breakdown } = unified_qualification;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-blue-50 border-blue-200';
    if (score >= 40) return 'bg-yellow-50 border-yellow-200';
    return 'bg-gray-50 border-gray-200';
  };

  return (
    <div className="space-y-6">
      {/* Unified Score Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-indigo-100 mb-1">
              Unified Qualification Score
            </div>
            <div className="text-5xl font-bold">
              {unified_qualification.unified_score}
              <span className="text-2xl text-indigo-200">/100</span>
            </div>
            <div className="text-sm text-indigo-100 mt-2">
              Multi-framework AI assessment
            </div>
          </div>
          <div className="text-right space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-indigo-100 text-sm">APEX:</span>
              <span className="font-bold text-xl">{unified_qualification.apex_score}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-indigo-100 text-sm">BANT:</span>
              <span className="font-bold text-xl">{unified_qualification.bant_score}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-indigo-100 text-sm">SPICE:</span>
              <span className="font-bold text-xl">{unified_qualification.spice_score}</span>
            </div>
          </div>
        </div>
      </div>

      {/* APEX Scores */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="bg-indigo-50 px-6 py-3 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-indigo-600" />
            <h3 className="font-semibold text-gray-900">APEX AI Scoring</h3>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-3 gap-4">
            <div className={`border rounded-lg p-4 ${getScoreBg(unified_qualification.mdcp_score)}`}>
              <div className={`text-3xl font-bold ${getScoreColor(unified_qualification.mdcp_score)}`}>
                {unified_qualification.mdcp_score}
              </div>
              <div className="text-sm font-medium text-gray-700 mt-1">MDCP</div>
              <div className="text-xs text-gray-600">Match, Data, Contact, Profile</div>
            </div>
            <div className={`border rounded-lg p-4 ${getScoreBg(unified_qualification.rss_score)}`}>
              <div className={`text-3xl font-bold ${getScoreColor(unified_qualification.rss_score)}`}>
                {unified_qualification.rss_score}
              </div>
              <div className="text-sm font-medium text-gray-700 mt-1">RSS</div>
              <div className="text-xs text-gray-600">Readiness, Suitability, Seniority</div>
            </div>
            <div className={`border rounded-lg p-4 ${getScoreBg(unified_qualification.apex_score)}`}>
              <div className={`text-3xl font-bold ${getScoreColor(unified_qualification.apex_score)}`}>
                {unified_qualification.apex_score}
              </div>
              <div className="text-sm font-medium text-gray-700 mt-1">APEX</div>
              <div className="text-xs text-gray-600">Composite Score</div>
            </div>
          </div>
        </div>
      </div>

      {/* BANT Framework */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="bg-blue-50 px-6 py-3 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold text-gray-900">BANT Qualification</h3>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
              bant_breakdown.qualification_status === 'HIGHLY_QUALIFIED' ? 'bg-green-100 text-green-800' :
              bant_breakdown.qualification_status === 'QUALIFIED' ? 'bg-blue-100 text-blue-800' :
              bant_breakdown.qualification_status === 'PARTIALLY_QUALIFIED' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {bant_breakdown.qualification_status.replace('_', ' ')}
            </span>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-4 gap-4 mb-4">
            {[
              { label: 'Budget', score: bant_breakdown.budget_score, max: 25 },
              { label: 'Authority', score: bant_breakdown.authority_score, max: 25 },
              { label: 'Need', score: bant_breakdown.need_score, max: 25 },
              { label: 'Timeline', score: bant_breakdown.timeline_score, max: 25 }
            ].map(({ label, score, max }) => (
              <div key={label} className="text-center">
                <div className={`text-3xl font-bold ${getScoreColor(score * 4)}`}>
                  {score}
                </div>
                <div className="text-sm font-medium text-gray-700 mt-1">{label}</div>
                <div className="text-xs text-gray-500">/{max}</div>
              </div>
            ))}
          </div>
          <div className="pt-4 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">Total BANT Score</span>
              <span className={`text-2xl font-bold ${getScoreColor(bant_breakdown.total_score)}`}>
                {bant_breakdown.total_score}/100
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* SPICE Framework */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="bg-purple-50 px-6 py-3 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-purple-600" />
              <h3 className="font-semibold text-gray-900">SPICE Assessment</h3>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
              spice_breakdown.qualification_status === 'ADVANCING' ? 'bg-purple-100 text-purple-800' :
              spice_breakdown.qualification_status === 'QUALIFIED' ? 'bg-blue-100 text-blue-800' :
              spice_breakdown.qualification_status === 'DEVELOPING' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {spice_breakdown.qualification_status}
            </span>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-5 gap-3 mb-4">
            {[
              { label: 'Situation', score: spice_breakdown.situation_score },
              { label: 'Problem', score: spice_breakdown.problem_score },
              { label: 'Implication', score: spice_breakdown.implication_score },
              { label: 'Critical Event', score: spice_breakdown.critical_event_score },
              { label: 'Decision', score: spice_breakdown.decision_score }
            ].map(({ label, score }) => (
              <div key={label} className="text-center">
                <div className={`text-2xl font-bold ${getScoreColor(score * 5)}`}>
                  {score}
                </div>
                <div className="text-xs font-medium text-gray-700 mt-1">{label}</div>
                <div className="text-xs text-gray-500">/20</div>
              </div>
            ))}
          </div>
          <div className="pt-4 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">Total SPICE Score</span>
              <span className={`text-2xl font-bold ${getScoreColor(spice_breakdown.total_score)}`}>
                {spice_breakdown.total_score}/100
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      {recommendation && (
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg overflow-hidden">
          <div className="px-6 py-3 bg-amber-100 border-b border-amber-200">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🎯</span>
              <h3 className="font-semibold text-gray-900">AI Recommendations</h3>
            </div>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-gray-600">Priority:</span>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                recommendation.priority === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                recommendation.priority === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                recommendation.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {recommendation.priority}
              </span>
            </div>
            
            <div>
              <div className="text-sm font-medium text-gray-600 mb-2">Next Best Action:</div>
              <div className="bg-white border border-amber-300 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-800 font-medium">
                    {recommendation.next_best_action}
                  </span>
                </div>
              </div>
            </div>

            {recommendation.recommended_actions && recommendation.recommended_actions.length > 0 && (
              <div>
                <div className="text-sm font-medium text-gray-600 mb-2">Recommended Actions:</div>
                <div className="space-y-2">
                  {recommendation.recommended_actions.map((action: string, idx: number) => (
                    <div key={idx} className="flex items-start gap-3 bg-white rounded-lg p-3 border border-amber-200">
                      <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{action}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default QualificationTab;
