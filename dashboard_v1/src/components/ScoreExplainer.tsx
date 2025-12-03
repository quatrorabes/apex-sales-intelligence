import React from 'react';
import { TrendingUp, Activity, Target, Info } from 'lucide-react';

interface ScoreExplainerProps {
  mdcpScore?: number;
  mdcpTier?: string;
  priorityScore?: number;
  urgencyLevel?: string;
  rssScore?: number;
}

export const ScoreExplainer: React.FC<ScoreExplainerProps> = ({
  mdcpScore = 0,
  mdcpTier = 'Unknown',
  priorityScore = 0,
  urgencyLevel = 'Unknown',
  rssScore = 0,
}) => {
  const getTierColor = (tier: string) => {
    switch (tier?.toLowerCase()) {
      case 'hot': return 'text-red-600 bg-red-50';
      case 'warm': return 'text-orange-600 bg-orange-50';
      case 'qualified': return 'text-yellow-600 bg-yellow-50';
      case 'nurture': return 'text-blue-600 bg-blue-50';
      case 'cold': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getUrgencyColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'urgent': return 'text-red-600 bg-red-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-blue-600 bg-blue-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="bg-white rounded-lg border p-4 space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Info className="h-5 w-5 text-blue-600" />
        <h3 className="font-semibold text-gray-900">Score Breakdown</h3>
      </div>

      <div className="space-y-3">
        {/* MDCP Score */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4 text-purple-600" />
            <span className="text-sm font-medium text-gray-700">MDCP Score</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-gray-900">{mdcpScore}</span>
            <span className={`px-2 py-1 rounded text-xs font-semibold ${getTierColor(mdcpTier)}`}>
              {mdcpTier}
            </span>
          </div>
        </div>

        {/* Priority Score */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">Priority Score</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-gray-900">{priorityScore}</span>
            <span className={`px-2 py-1 rounded text-xs font-semibold ${getUrgencyColor(urgencyLevel)}`}>
              {urgencyLevel}
            </span>
          </div>
        </div>

        {/* RSS Score */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-green-600" />
            <span className="text-sm font-medium text-gray-700">Relationship Strength</span>
          </div>
          <span className="text-lg font-bold text-gray-900">{rssScore}</span>
        </div>
      </div>

      <div className="mt-4 p-3 bg-blue-50 rounded text-sm text-blue-800">
        <p className="font-medium mb-1">What these scores mean:</p>
        <ul className="space-y-1 text-xs">
          <li>• <strong>MDCP:</strong> Likelihood to convert (0-100)</li>
          <li>• <strong>Priority:</strong> Urgency of outreach</li>
          <li>• <strong>RSS:</strong> Relationship health (0-100)</li>
        </ul>
      </div>
    </div>
  );
};
