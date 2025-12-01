import React, { useState, useEffect } from 'react';
import { Phone, Mail, Linkedin, Users, Clock, CheckCircle, XCircle } from 'lucide-react';

interface Activity {
  id: number;
  activity_type: string;
  activity_date: string;
  direction: string;
  outcome: string;
  notes: string;
}

interface ActivityTimelineProps {
  contactId: number;
}

export default function ActivityTimeline({ contactId }: ActivityTimelineProps) {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/activities/${contactId}`);
        const data = await res.json();
        if (data.success) {
          setActivities(data.activities);
        }
      } catch (err) {
        console.error('Failed to fetch activities:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchActivities();
  }, [contactId]);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'call': return <Phone size={16} />;
      case 'email': return <Mail size={16} />;
      case 'linkedin': return <Linkedin size={16} />;
      case 'meeting': return <Users size={16} />;
      default: return <Clock size={16} />;
    }
  };

  const getOutcomeColor = (outcome: string) => {
    if (outcome.toLowerCase().includes('connected') || outcome.toLowerCase().includes('scheduled')) {
      return '#22c55e';
    }
    if (outcome.toLowerCase().includes('voicemail') || outcome.toLowerCase().includes('no answer')) {
      return '#eab308';
    }
    return '#6b7280';
  };

  if (loading) {
    return <div style={{ padding: 20, textAlign: 'center', color: '#9ca3af' }}>Loading timeline...</div>;
  }

  if (activities.length === 0) {
    return <div style={{ padding: 20, textAlign: 'center', color: '#9ca3af' }}>No activities logged yet</div>;
  }

  return (
    <div style={{ background: 'rgba(30,41,59,0.5)', borderRadius: 12, padding: 20, border: '1px solid rgba(148,163,184,0.2)' }}>
      <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16, color: '#e5e7eb' }}>
        Activity Timeline ({activities.length})
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {activities.map((activity) => (
          <div
            key={activity.id}
            style={{
              display: 'flex',
              gap: 12,
              padding: 12,
              background: 'rgba(15,23,42,0.6)',
              borderRadius: 8,
              border: '1px solid rgba(148,163,184,0.2)',
            }}
          >
            <div style={{ color: '#a5b4fc', marginTop: 2 }}>
              {getActivityIcon(activity.activity_type)}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span style={{ fontSize: 14, fontWeight: 600, color: '#e5e7eb' }}>
                  {activity.activity_type.charAt(0).toUpperCase() + activity.activity_type.slice(1)}
                </span>
                <span style={{ fontSize: 12, color: '#9ca3af' }}>
                  {new Date(activity.activity_date).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </span>
              </div>
              <div style={{ fontSize: 13, color: getOutcomeColor(activity.outcome), marginBottom: 4 }}>
                {activity.outcome}
              </div>
              {activity.notes && (
                <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 6 }}>
                  {activity.notes}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
