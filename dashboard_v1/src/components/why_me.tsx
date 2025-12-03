import React from 'react';
import { Target, TrendingUp, Users, Zap } from 'lucide-react';

interface WhyMeProps {
  data: {
    persona_match?: string;
    value_alignment?: string[];
    opportunity_signals?: string[];
    relationship_strength?: number;
    recommended_talking_points?: string[];
  };
}

export const WhyMe: React.FC<WhyMeProps> = ({ data }) => {
  const {
    persona_match,
    value_alignment = [],
    opportunity_signals = [],
    relationship_strength = 0,
    recommended_talking_points = [],
  } = data;

  return (
    <div className="space-y-6">
      {/* Persona Match */}
      {persona_match && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Target className="h-5 w-5 text-purple-600" />
            <h3 className="font-semibold text-gray-900">Persona Match</h3>
          </div>
          <p className="text-gray-700">{persona_match}</p>
        </div>
      )}

      {/* Value Alignment */}
      {value_alignment.length > 0 && (
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="h-5 w-5 text-green-600" />
            <h3 className="font-semibold text-gray-900">Value Alignment</h3>
          </div>
          <ul className="space-y-2">
            {value_alignment.map((item, index) => (
              <li key={index} className="flex items-start gap-2 text-gray-700">
                <span className="text-green-600 mt-0.5">✓</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Opportunity Signals */}
      {opportunity_signals.length > 0 && (
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="h-5 w-5 text-amber-600" />
            <h3 className="font-semibold text-gray-900">Opportunity Signals</h3>
          </div>
          <ul className="space-y-2">
            {opportunity_signals.map((signal, index) => (
              <li key={index} className="flex items-start gap-2 text-gray-700">
                <span className="text-amber-600 mt-0.5">⚡</span>
                <span>{signal}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Relationship Strength */}
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Users className="h-5 w-5 text-blue-600" />
          <h3 className="font-semibold text-gray-900">Relationship Strength</h3>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex-1 bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all"
              style={{ width: `${relationship_strength}%` }}
            />
          </div>
          <span className="text-lg font-bold text-gray-900">{relationship_strength}%</span>
        </div>
      </div>

      {/* Recommended Talking Points */}
      {recommended_talking_points.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-3">Recommended Talking Points</h3>
          <ol className="space-y-2">
            {recommended_talking_points.map((point, index) => (
              <li key={index} className="flex gap-2 text-blue-800">
                <span className="font-semibold">{index + 1}.</span>
                <span>{point}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
};

export default WhyMe;
