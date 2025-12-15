import React, { useState } from 'react';
import { Phone, Mail, Calendar, FileText, Send } from 'lucide-react';

interface ActivityLoggerProps {
  contactId: number;
  onActivityLogged?: (activity: any) => void;
}

export const ActivityLogger: React.FC<ActivityLoggerProps> = ({ contactId, onActivityLogged }) => {
  const [activityType, setActivityType] = useState<'call' | 'email' | 'meeting' | 'note'>('note');
  const [notes, setNotes] = useState('');
  const [outcome, setOutcome] = useState('');
  const [isLogging, setIsLogging] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLogging(true);

    try {
      const activity = {
        type: activityType,
        notes,
        outcome,
        timestamp: new Date().toISOString(),
      };

      // API call would go here
      console.log('Logging activity:', activity);
      
      onActivityLogged?.(activity);
      
      // Reset form
      setNotes('');
      setOutcome('');
    } catch (error) {
      console.error('Failed to log activity:', error);
    } finally {
      setIsLogging(false);
    }
  };

  const activityTypes = [
    { value: 'call', label: 'Phone Call', icon: Phone },
    { value: 'email', label: 'Email', icon: Mail },
    { value: 'meeting', label: 'Meeting', icon: Calendar },
    { value: 'note', label: 'Note', icon: FileText },
  ];

  return (
    <div className="bg-white rounded-lg border p-4">
      <h3 className="font-semibold text-gray-900 mb-4">Log Activity</h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Activity Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Activity Type
          </label>
          <div className="grid grid-cols-4 gap-2">
            {activityTypes.map(({ value, label, icon: Icon }) => (
              <button
                key={value}
                type="button"
                onClick={() => setActivityType(value as any)}
                className={`flex flex-col items-center gap-1 p-3 rounded-lg border-2 transition ${
                  activityType === value
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300 text-gray-600'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="text-xs font-medium">{label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="What happened during this interaction?"
            required
          />
        </div>

        {/* Outcome */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Outcome
          </label>
          <select
            value={outcome}
            onChange={(e) => setOutcome(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select outcome...</option>
            <option value="interested">Interested</option>
            <option value="follow_up">Follow-up Scheduled</option>
            <option value="not_interested">Not Interested</option>
            <option value="no_response">No Response</option>
            <option value="meeting_scheduled">Meeting Scheduled</option>
          </select>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLogging}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          <Send className="h-4 w-4" />
          {isLogging ? 'Logging...' : 'Log Activity'}
        </button>
      </form>
    </div>
  );
};
