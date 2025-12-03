import React from 'react';
import { Calendar, Phone, Mail, MessageSquare, FileText } from 'lucide-react';

interface Activity {
  id: string;
  type: 'call' | 'email' | 'meeting' | 'note';
  title: string;
  description: string;
  timestamp: string;
}

interface ActivityTimelineProps {
  activities: Activity[];
}

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({ activities }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'call': return <Phone className="h-4 w-4" />;
      case 'email': return <Mail className="h-4 w-4" />;
      case 'meeting': return <Calendar className="h-4 w-4" />;
      case 'note': return <FileText className="h-4 w-4" />;
      default: return <MessageSquare className="h-4 w-4" />;
    }
  };

  const getColor = (type: string) => {
    switch (type) {
      case 'call': return 'bg-green-100 text-green-600';
      case 'email': return 'bg-blue-100 text-blue-600';
      case 'meeting': return 'bg-purple-100 text-purple-600';
      case 'note': return 'bg-gray-100 text-gray-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="space-y-4">
      {activities.map((activity, index) => (
        <div key={activity.id} className="flex gap-3">
          <div className="relative">
            <div className={`flex items-center justify-center h-8 w-8 rounded-full ${getColor(activity.type)}`}>
              {getIcon(activity.type)}
            </div>
            {index < activities.length - 1 && (
              <div className="absolute top-8 left-1/2 -translate-x-1/2 w-0.5 h-full bg-gray-200" />
            )}
          </div>
          <div className="flex-1 pb-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="font-medium text-gray-900">{activity.title}</p>
                <p className="text-sm text-gray-600 mt-1">{activity.description}</p>
              </div>
              <span className="text-xs text-gray-500 whitespace-nowrap ml-2">
                {new Date(activity.timestamp).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
