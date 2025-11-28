import React, { useState, useEffect } from 'react';
import { TrendingUp, Zap, RefreshCw, Eye } from 'lucide-react';

interface Signal {
  id: number;
  contact_id: number;
  name: string;
  company: string;
  signal_type: string;
  signal_data: string;
  urgency_boost: number;
  signal_date: string;
}

export default function SignalsFeed() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);

  const fetchSignals = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/api/signals/unread');
      const data = await res.json();
      if (data.success) {
        setSignals(data.signals);
      }
    } catch (err) {
      console.error('Failed to fetch signals:', err);
    } finally {
      setLoading(false);
    }
  };

  const scanForSignals = async () => {
    setScanning(true);
    try {
      const res = await fetch('http://localhost:8000/api/signals/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      const data = await res.json();
      if (data.success) {
        fetchSignals();
      }
    } catch (err) {
      console.error('Failed to scan signals:', err);
    } finally {
      setScanning(false);
    }
  };

  const markAsRead = async (signalId: number) => {
    try {
      await fetch(`http://localhost:8000/api/signals/mark-read/${signalId}`, {
        method: 'POST',
      });
      setSignals(signals.filter((s) => s.id !== signalId));
    } catch (err) {
      console.error('Failed to mark signal:', err);
    }
  };

  useEffect(() => {
    fetchSignals();
  }, []);

  const getSignalEmoji = (type: string) => {
    switch (type) {
      case 'job_change': return '📢';
      case 'linkedin_post': return '💬';
      case 'company_news': return '📰';
      case 'funding': return '💰';
      default: return '💡';
    }
  };

  return (
    <div style={{ background: 'rgba(30,41,59,0.5)', borderRadius: 12, padding: 20, border: '1px solid rgba(148,163,184,0.2)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, color: '#e5e7eb', display: 'flex', alignItems: 'center', gap: 8 }}>
          <TrendingUp size={20} />
          Opportunity Signals ({signals.length})
        </h3>
        <button
          onClick={scanForSignals}
          disabled={scanning}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '8px 12px',
            borderRadius: 6,
            border: '1px solid rgba(99,102,241,0.5)',
            background: scanning ? 'rgba(71,85,105,0.5)' : 'rgba(99,102,241,0.2)',
            color: '#a5b4fc',
            fontSize: 12,
            fontWeight: 600,
            cursor: scanning ? 'not-allowed' : 'pointer',
          }}
        >
          <RefreshCw size={14} style={{ animation: scanning ? 'spin 1s linear infinite' : 'none' }} />
          {scanning ? 'Scanning...' : 'Scan Now'}
        </button>
      </div>

      {loading ? (
        <div style={{ padding: 20, textAlign: 'center', color: '#9ca3af' }}>Loading signals...</div>
      ) : signals.length === 0 ? (
        <div style={{ padding: 20, textAlign: 'center', color: '#9ca3af' }}>
          No new signals. Click "Scan Now" to detect opportunities.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {signals.map((signal) => (
            <div
              key={signal.id}
              style={{
                padding: 12,
                background: 'rgba(15,23,42,0.6)',
                borderRadius: 8,
                border: '1px solid rgba(148,163,184,0.2)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <span style={{ fontSize: 20 }}>{getSignalEmoji(signal.signal_type)}</span>
                  <span style={{ fontSize: 14, fontWeight: 600, color: '#e5e7eb' }}>
                    {signal.name}
                  </span>
                  <span style={{ fontSize: 12, color: '#9ca3af' }}>at {signal.company}</span>
                </div>
                <div style={{ fontSize: 13, color: '#cbd5e1', marginBottom: 6 }}>
                  {signal.signal_data}
                </div>
                <div style={{ fontSize: 11, color: '#9ca3af' }}>
                  +{signal.urgency_boost} urgency boost • {new Date(signal.signal_date).toLocaleString()}
                </div>
              </div>
              <button
                onClick={() => markAsRead(signal.id)}
                style={{
                  padding: '6px 10px',
                  borderRadius: 6,
                  border: '1px solid rgba(148,163,184,0.3)',
                  background: 'rgba(15,23,42,0.6)',
                  color: '#9ca3af',
                  fontSize: 11,
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                }}
              >
                <Eye size={12} />
                Mark Read
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
