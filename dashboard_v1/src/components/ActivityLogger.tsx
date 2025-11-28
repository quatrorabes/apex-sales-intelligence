import React, { useState } from 'react';
import { Phone, Mail, Linkedin, Users, CheckCircle, Clock } from 'lucide-react';

interface ActivityLoggerProps {
  contactId: number;
  contactName: string;
  onActivityLogged?: () => void;
}

export default function ActivityLogger({ contactId, contactName, onActivityLogged }: ActivityLoggerProps) {
  const [activityType, setActivityType] = useState<'call' | 'email' | 'linkedin' | 'meeting'>('call');
  const [outcome, setOutcome] = useState('');
  const [notes, setNotes] = useState('');
  const [logging, setLogging] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLogging(true);

    try {
      const res = await fetch('http://localhost:8000/api/activities/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contact_id: contactId,
          activity_type: activityType,
          activity_date: new Date().toISOString(),
          direction: 'outbound',
          outcome,
          notes,
        }),
      });

      const data = await res.json();

      if (data.success) {
        setSuccess(true);
        setNotes('');
        setOutcome('');
        onActivityLogged?.();
        setTimeout(() => setSuccess(false), 3000);
      }
    } catch (err) {
      console.error('Failed to log activity:', err);
    } finally {
      setLogging(false);
    }
  };

  const activityOptions = [
    { value: 'call', label: '📞 Call', icon: Phone },
    { value: 'email', label: '📧 Email', icon: Mail },
    { value: 'linkedin', label: '💼 LinkedIn', icon: Linkedin },
    { value: 'meeting', label: '👥 Meeting', icon: Users },
  ];

  const outcomeOptions = {
    call: ['Connected', 'Voicemail', 'No Answer', 'Wrong Number'],
    email: ['Sent', 'Replied', 'Bounced', 'Opened'],
    linkedin: ['Message Sent', 'Connection Request', 'Endorsed', 'Comment'],
    meeting: ['Scheduled', 'Completed', 'Rescheduled', 'Cancelled'],
  };

  return (
    <div style={{ background: 'rgba(30,41,59,0.5)', borderRadius: 12, padding: 20, border: '1px solid rgba(148,163,184,0.2)' }}>
      <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16, color: '#e5e7eb' }}>
        Log Activity with {contactName}
      </h3>

      <form onSubmit={handleSubmit}>
        {/* Activity Type */}
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 500, marginBottom: 8, color: '#9ca3af' }}>
            Activity Type
          </label>
          <div style={{ display: 'flex', gap: 8 }}>
            {activityOptions.map((option) => {
              const Icon = option.icon;
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setActivityType(option.value as any)}
                  style={{
                    flex: 1,
                    padding: '10px 12px',
                    borderRadius: 8,
                    border: activityType === option.value ? '2px solid rgba(99,102,241,0.8)' : '1px solid rgba(148,163,184,0.3)',
                    background: activityType === option.value ? 'rgba(99,102,241,0.2)' : 'rgba(15,23,42,0.6)',
                    color: activityType === option.value ? '#a5b4fc' : '#9ca3af',
                    fontSize: 13,
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 6,
                  }}
                >
                  <Icon size={16} />
                  {option.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Outcome */}
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 500, marginBottom: 8, color: '#9ca3af' }}>
            Outcome
          </label>
          <select
            value={outcome}
            onChange={(e) => setOutcome(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: 8,
              border: '1px solid rgba(148,163,184,0.3)',
              background: 'rgba(15,23,42,0.6)',
              color: '#e5e7eb',
              fontSize: 14,
            }}
          >
            <option value="">Select outcome...</option>
            {outcomeOptions[activityType].map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        </div>

        {/* Notes */}
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', fontSize: 13, fontWeight: 500, marginBottom: 8, color: '#9ca3af' }}>
            Notes
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add notes..."
            rows={3}
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: 8,
              border: '1px solid rgba(148,163,184,0.3)',
              background: 'rgba(15,23,42,0.6)',
              color: '#e5e7eb',
              fontSize: 14,
              resize: 'vertical',
            }}
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={logging || !outcome}
          style={{
            width: '100%',
            padding: '12px',
            borderRadius: 8,
            border: 'none',
            background: success
              ? 'linear-gradient(135deg, rgba(34,197,94,0.5), rgba(22,163,74,0.5))'
              : logging || !outcome
              ? 'rgba(71,85,105,0.5)'
              : 'linear-gradient(135deg, rgba(99,102,241,0.6), rgba(79,70,229,0.6))',
            color: '#e5e7eb',
            fontSize: 14,
            fontWeight: 600,
            cursor: logging || !outcome ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
          }}
        >
          {success ? (
            <>
              <CheckCircle size={18} />
              Activity Logged!
            </>
          ) : logging ? (
            <>
              <Clock size={18} />
              Logging...
            </>
          ) : (
            'Log Activity'
          )}
        </button>
      </form>
    </div>
  );
}
