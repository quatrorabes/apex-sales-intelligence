import React, { useEffect, useState } from 'react';
import { X, Loader2, CheckCircle2 } from 'lucide-react';

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'https://apex-backend-i7b0.onrender.com';

interface EnrollCadenceModalProps {
  isOpen: boolean;
  onClose: () => void;
  contactId: string;
  contactName: string;
}

export function EnrollCadenceModal({ isOpen, onClose, contactId, contactName }: EnrollCadenceModalProps) {
  const [cadences, setCadences] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [enrolling, setEnrolling] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    setLoading(true);
    fetch(`${API_BASE}/api/cadences`)
      .then(res => res.json())
      .then(data => setCadences(data.cadences || data || []))
      .catch(() => setCadences([]))
      .finally(() => setLoading(false));
  }, [isOpen]);

  const handleEnroll = async () => {
    if (!selectedId) return;
    setEnrolling(true);
    try {
      const res = await fetch(`${API_BASE}/api/v2/contacts/${contactId}/enroll-cadence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cadence_id: selectedId })
      });
      if (res.ok) {
        setSuccess(true);
        setTimeout(() => { onClose(); setSuccess(false); setSelectedId(null); }, 1500);
      }
    } catch (err) {
      alert('Enrollment failed');
    } finally {
      setEnrolling(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-slate-900 rounded-lg border border-slate-800 shadow-2xl w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div>
            <h2 className="text-xl font-semibold text-slate-100">Enroll in Sales Cadence</h2>
            <p className="text-sm text-slate-400 mt-1">Start a sales sequence for {contactName}</p>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-slate-800 transition-colors">
            <X className="h-5 w-5 text-slate-400" />
          </button>
        </div>
        <div className="flex-1 overflow-auto px-6 py-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-sky-400" />
            </div>
          ) : success ? (
            <div className="flex flex-col items-center justify-center py-12 text-emerald-400">
              <CheckCircle2 className="h-16 w-16 mb-4" />
              <p className="text-lg font-semibold">Successfully Enrolled!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {cadences.map(c => (
                <button key={c.id} onClick={() => setSelectedId(c.id)} className={`w-full text-left p-4 rounded-lg border transition-all ${selectedId === c.id ? 'border-sky-500 bg-sky-500/10' : 'border-slate-800 hover:border-slate-700 bg-slate-950/60'}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-semibold text-slate-100 mb-1">{c.name}</div>
                      <div className="text-sm text-slate-400 mb-2">{c.description}</div>
                      <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span>📧 {c.steps} steps</span>
                        <span>⏱️ {c.duration_days} days</span>
                      </div>
                    </div>
                    {selectedId === c.id && <CheckCircle2 className="h-5 w-5 text-sky-400 mt-1" />}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="px-6 py-4 border-t border-slate-800 flex items-center justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 transition-colors">Cancel</button>
          <button onClick={handleEnroll} disabled={!selectedId || enrolling} className="px-6 py-2 bg-sky-500 hover:bg-sky-600 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center gap-2">
            {enrolling ? <><Loader2 className="h-4 w-4 animate-spin" />Enrolling...</> : 'Enroll in Cadence'}
          </button>
        </div>
      </div>
    </div>
  );
}
