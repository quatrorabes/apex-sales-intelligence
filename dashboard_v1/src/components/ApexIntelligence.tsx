import React, { useState, useEffect } from 'react';
import { Brain, Zap, TrendingUp, Users, Target, Loader, AlertCircle } from 'lucide-react';
import { getContact, getContacts, enrichContact, getStats } from '@/config/api';
import { Contact } from '../types';

interface ApexInsight {
  type: 'opportunity' | 'risk' | 'recommendation' | 'trend';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  contacts?: Contact[];
}

export const ApexIntelligence: React.FC = () => {
  const [insights, setInsights] = useState<ApexInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    setLoading(true);
    setError(null);
    try {
      // Mock insights for now - replace with real API call
      const mockInsights: ApexInsight[] = [
        {
          type: 'opportunity',
          title: '12 Hot Prospects Need Immediate Attention',
          description: 'You have 12 contacts with MDCP scores above 80 who haven\'t been contacted in the last 7 days.',
          priority: 'high',
        },
        {
          type: 'risk',
          title: '5 Warm Relationships Cooling Down',
          description: 'These contacts show declining engagement. Reach out this week to maintain momentum.',
          priority: 'medium',
        },
        {
          type: 'recommendation',
          title: 'Best Time to Reach Out: Tuesday 10-11 AM',
          description: 'Based on historical engagement data, your contacts are most responsive during this window.',
          priority: 'low',
        },
        {
          type: 'trend',
          title: 'SBA Banker Persona Shows 35% Higher Conversion',
          description: 'Focus on enriching and prioritizing contacts in this persona segment.',
          priority: 'medium',
        },
      ];
      
      setInsights(mockInsights);
    } catch (err: any) {
      console.error('Failed to load insights:', err);
      setError(err.message || 'Failed to load intelligence');
    } finally {
      setLoading(false);
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'opportunity': return <Target className="h-6 w-6" />;
      case 'risk': return <AlertCircle className="h-6 w-6" />;
      case 'recommendation': return <Zap className="h-6 w-6" />;
      case 'trend': return <TrendingUp className="h-6 w-6" />;
      default: return <Brain className="h-6 w-6" />;
    }
  };

  const getColor = (type: string) => {
    switch (type) {
      case 'opportunity': return 'bg-green-100 text-green-700 border-green-300';
      case 'risk': return 'bg-red-100 text-red-700 border-red-300';
      case 'recommendation': return 'bg-blue-100 text-blue-700 border-blue-300';
      case 'trend': return 'bg-purple-100 text-purple-700 border-purple-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const getPriorityBadge = (priority: string) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-gray-100 text-gray-800',
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-semibold ${colors[priority as keyof typeof colors]}`}>
        {priority.toUpperCase()}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <Loader className="h-12 w-12 animate-spin text-blue-600 mb-4" />
        <p className="text-gray-600">Analyzing your pipeline...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-center">
        <AlertCircle className="h-16 w-16 text-red-500 mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Failed to Load Intelligence</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={loadInsights}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
        <div className="flex items-center gap-3 mb-2">
          <Brain className="h-8 w-8" />
          <h1 className="text-2xl font-bold">Apex Intelligence</h1>
        </div>
        <p className="text-purple-100">
          AI-powered insights and recommendations for your sales pipeline
        </p>
      </div>

      {/* Insights Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {insights.map((insight, index) => (
          <div key={index} className="bg-white border rounded-lg p-6 hover:shadow-lg transition">
            <div className="flex items-start gap-4">
              <div className={`p-3 rounded-lg border ${getColor(insight.type)}`}>
                {getIcon(insight.type)}
              </div>
              <div className="flex-1">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900 text-lg">{insight.title}</h3>
                  {getPriorityBadge(insight.priority)}
                </div>
                <p className="text-gray-600 mb-4">{insight.description}</p>
                <button className="text-blue-600 hover:text-blue-800 font-medium text-sm">
                  View Details →
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Target className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium text-gray-600">Hot Prospects</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">12</p>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-600">Avg MDCP Score</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">67</p>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Users className="h-5 w-5 text-purple-600" />
            <span className="text-sm font-medium text-gray-600">Active Contacts</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">84</p>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="h-5 w-5 text-amber-600" />
            <span className="text-sm font-medium text-gray-600">This Week</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">23</p>
        </div>
      </div>
    </div>
  );
};

export default ApexIntelligence;
