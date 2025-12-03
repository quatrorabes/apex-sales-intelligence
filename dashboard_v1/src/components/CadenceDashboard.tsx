import React, { useState } from 'react';
import { Calendar, Clock, CheckCircle2, AlertCircle, TrendingUp } from 'lucide-react';

interface CadenceStep {
  id: string;
  day: number;
  action: 'email' | 'call' | 'linkedin' | 'follow-up';
  status: 'pending' | 'completed' | 'skipped';
  dueDate?: string;
  completedDate?: string;
}

interface CadenceContact {
  id: number;
  name: string;
  company: string;
  currentDay: number;
  steps: CadenceStep[];
}

export const CadenceDashboard: React.FC = () => {
  const [contacts, setContacts] = useState<CadenceContact[]>([
    {
      id: 1,
      name: 'John Smith',
      company: 'Tech Corp',
      currentDay: 3,
      steps: [
        { id: '1', day: 1, action: 'email', status: 'completed', completedDate: '2024-12-01' },
        { id: '2', day: 2, action: 'linkedin', status: 'completed', completedDate: '2024-12-02' },
        { id: '3', day: 3, action: 'call', status: 'pending', dueDate: '2024-12-03' },
        { id: '4', day: 5, action: 'follow-up', status: 'pending', dueDate: '2024-12-05' },
      ],
    },
  ]);

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'email': return '📧';
      case 'call': return '📞';
      case 'linkedin': return '💼';
      case 'follow-up': return '🔄';
      default: return '📝';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'skipped': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <div className="flex items-center gap-3 mb-2">
          <Calendar className="h-8 w-8" />
          <h1 className="text-2xl font-bold">Cadence Dashboard</h1>
        </div>
        <p className="text-blue-100">
          Track and manage your outreach sequences
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-600">In Progress</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">8</p>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium text-gray-600">Completed</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">24</p>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <span className="text-sm font-medium text-gray-600">Due Today</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">5</p>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-5 w-5 text-purple-600" />
            <span className="text-sm font-medium text-gray-600">Response Rate</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">32%</p>
        </div>
      </div>

      {/* Contacts in Cadence */}
      <div className="space-y-4">
        {contacts.map((contact) => (
          <div key={contact.id} className="bg-white border rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold text-gray-900">{contact.name}</h3>
                <p className="text-sm text-gray-600">{contact.company}</p>
              </div>
              <span className="text-sm text-gray-500">Day {contact.currentDay}</span>
            </div>

            <div className="space-y-2">
              {contact.steps.map((step, index) => (
                <div
                  key={step.id}
                  className="flex items-center gap-3 p-3 rounded-lg bg-gray-50"
                >
                  <span className="text-2xl">{getActionIcon(step.action)}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 capitalize">
                        Day {step.day}: {step.action}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getStatusColor(step.status)}`}>
                        {step.status}
                      </span>
                    </div>
                    {step.dueDate && (
                      <p className="text-sm text-gray-500 mt-1">
                        Due: {new Date(step.dueDate).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  {step.status === 'pending' && (
                    <button className="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 transition text-sm">
                      Complete
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CadenceDashboard;
