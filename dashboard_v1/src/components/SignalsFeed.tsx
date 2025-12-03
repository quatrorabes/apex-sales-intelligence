import React from 'react';
import { TrendingUp, Briefcase, Award, DollarSign, Users, AlertCircle } from 'lucide-react';

interface Signal {
  id: string;
  type: 'job_change' | 'funding' | 'expansion' | 'leadership' | 'other';
  title: string;
  description: string;
  timestamp: string;
  contactId: number;
  contactName: string;
}

interface SignalsFeedProps {
  signals: Signal[];
  onSignalClick?: (signal: Signal) => void;
}

export const SignalsFeed: React.FC<SignalsFeedProps> = ({ signals, onSignalClick }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'job_change': return <Briefcase className="h-5 w-5" />;
      case 'funding': return <DollarSign className="h-5 w-5" />;
      case 'expansion': return <TrendingUp className="h-5 w-5" />;
      case 'leadership': return <Award className="h-5 w-5" />;
      case 'other': return <AlertCircle className="h-5 w-5" />;
      default: return <Users className="h-5 w-5" />;
    }
  };

  const getColor = (type: string) => {
    switch (type) {
      case 'job_change': return 'bg-purple-100 text-purple-600 border-purple-200';
      case 'funding': return 'bg-green-100 text-green-600 border-green-200';
      case 'expansion': return 'bg-blue-100 text-blue-600 border-blue-200';
      case 'leadership': return 'bg-amber-100 text-amber-600 border-amber-200';
      default: return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  if (!signals || signals.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <AlertCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
        <p>No signals detected</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {signals.map((signal) => (
        <div
          key={signal.id}
          onClick={() => onSignalClick?.(signal)}
          className="bg-white border rounded-lg p-4 hover:shadow-md transition cursor-pointer"
        >
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-lg border ${getColor(signal.type)}`}>
              {getIcon(signal.type)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 mb-1">{signal.title}</h4>
                  <p className="text-sm text-gray-600 line-clamp-2">{signal.description}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs font-medium text-blue-600">{signal.contactName}</span>
                    <span className="text-xs text-gray-400">•</span>
                    <span className="text-xs text-gray-500">
                      {new Date(signal.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
