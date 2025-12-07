// =============================================================================
// EnrollCadenceModal.tsx - Modal to enroll contact in a cadence
// =============================================================================

import { useState, useEffect } from 'react';
import { X, Play, Clock, Mail, Phone, Linkedin, Check, Loader2 } from 'lucide-react';

interface Cadence {
  id: number;
  name: string;
  description: string;
  steps: Array<{
    day: number;
    channel: string;
    template: string;
    title: string;
  }>;
}

interface Props {
  contactId: number;
  contactName: string;
  isOpen: boolean;
  onClose: () => void;
  onEnrolled: () => void;
}

const CHANNEL_ICONS: Record<string, React.ReactNode> = {
  email: <Mail size={14} />,
  call: <Phone size={14} />,
  linkedin: <Linkedin size={14} />
};

export default function EnrollCadenceModal({ contactId, contactName, isOpen, onClose, onEnrolled }: Props) {
  const [cadences, setCadences] = useState<Cadence[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchCadences();
    }
  }, [isOpen]);

  const fetchCadences = async () => {
    try {
      const res = await fetch('https://apex-backend-production-production.up.railway.app/api/cadences');
      const data = await res.json();
      setCadences(data.cadences || []);
      if (data.cadences?.length > 0) {
        setSelectedId(data.cadences[0].id);
      }
    } catch (e) {
      console.error('Failed to fetch cadences:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async () => {
    if (!selectedId) return;
    
    setEnrolling(true);
    try {
      const res = await fetch(`https://apex-backend-production-production.up.railway.app/api/contacts/${contactId}/enroll`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cadence_id: selectedId })
      });
      
      const data = await res.json();
      
      if (data.success) {
        onEnrolled();
        onClose();
      } else {
        alert(data.error || 'Failed to enroll');
      }
    } catch (e) {
      console.error('Enrollment failed:', e);
    } finally {
      setEnrolling(false);
    }
  };

  if (!isOpen) return null;

  const selectedCadence = cadences.find(c => c.id === selectedId);

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-[#161b22] border border-[#30363d] rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#30363d] flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">Start Cadence</h2>
            <p className="text-sm text-[#8b919a]">Enroll {contactName} in an outreach sequence</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-[#21262d] rounded-lg text-[#8b919a]">
            <X size={20} />
          </button>
        </div>
        
        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin text-indigo-500" size={32} />
            </div>
          ) : (
            <div className="space-y-4">
              {/* Cadence Selection */}
              <div className="space-y-3">
                {cadences.map(cadence => (
                  <button
                    key={cadence.id}
                    onClick={() => setSelectedId(cadence.id)}
                    className={`w-full text-left p-4 rounded-xl border transition-all ${
                      selectedId === cadence.id
                        ? 'bg-indigo-600/20 border-indigo-500/50'
                        : 'bg-[#0d1117] border-[#30363d] hover:border-[#484f58]'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-white">{cadence.name}</h3>
                        <p className="text-sm text-[#8b919a] mt-1">{cadence.description}</p>
                      </div>
                      {selectedId === cadence.id && (
                        <div className="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center">
                          <Check size={14} />
                        </div>
                      )}
                    </div>
                    
                                  {/* Steps Preview */}
                    <div className="flex items-center gap-2 mt-3 flex-wrap">
                      {cadence.steps.map((step, i) => (
                        <div
                          key={i}
                          className={`flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs ${
                            step.channel === 'email' ? 'bg-indigo-500/20 text-indigo-300' :
                            step.channel === 'call' ? 'bg-emerald-500/20 text-emerald-300' :
                            'bg-blue-500/20 text-blue-300'
                          }`}
                        >
                          {CHANNEL_ICONS[step.channel]}
                          <span>Day {step.day}</span>
                        </div>
                      ))}
                    </div>
                  </button>
                ))}
              </div>

              {/* Selected Cadence Details */}
              {selectedCadence && (
                <div className="mt-6 p-4 bg-[#0d1117] border border-[#30363d] rounded-xl">
                  <h4 className="text-sm font-medium text-white mb-3">Sequence Timeline</h4>
                  <div className="space-y-2">
                    {selectedCadence.steps.map((step, i) => (
                      <div key={i} className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                          step.channel === 'email' ? 'bg-indigo-500/20 text-indigo-400' :
                          step.channel === 'call' ? 'bg-emerald-500/20 text-emerald-400' :
                          'bg-blue-500/20 text-blue-400'
                        }`}>
                          {CHANNEL_ICONS[step.channel]}
                        </div>
                        <div className="flex-1">
                          <p className="text-sm text-white">{step.title}</p>
                          <p className="text-xs text-[#6e7681]">Day {step.day} • {step.channel}</p>
                        </div>
                        {i < selectedCadence.steps.length - 1 && (
                          <div className="w-px h-4 bg-[#30363d] ml-4 -mb-6 relative top-4" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="px-6 py-4 border-t border-[#30363d] flex items-center justify-between bg-[#0d1117]">
          <p className="text-sm text-[#8b919a]">
            {selectedCadence ? `${selectedCadence.steps.length} steps over ${selectedCadence.steps[selectedCadence.steps.length - 1]?.day || 0} days` : ''}
          </p>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-[#21262d] hover:bg-[#30363d] rounded-lg text-sm font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleEnroll}
              disabled={!selectedId || enrolling}
              className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-lg text-sm font-medium flex items-center gap-2 disabled:opacity-50"
            >
              {enrolling ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Enrolling...
                </>
              ) : (
                <>
                  <Play size={16} />
                  Start Cadence
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
