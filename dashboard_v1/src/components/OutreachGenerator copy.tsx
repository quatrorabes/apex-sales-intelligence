// =============================================================================
// OutreachGenerator.tsx - Triple-Channel AI Outreach Suite
// =============================================================================
// Email + LinkedIn + Call Scripts | Playbook-Powered | Personality-Adapted
// =============================================================================

import { useState } from 'react';
import {
  Mail, MessageSquare, Sparkles, Copy, RefreshCw, Check,
  Send, Zap, Target, Brain, ChevronDown, Linkedin, Phone,
  Clock, FileText, Loader2, Settings, ThumbsUp, AlertCircle, 
  Wand2, Layers, MessageCircle, HelpCircle, Shield, ChevronRight,
  Mic, PhoneCall, Voicemail, Users
} from 'lucide-react';

interface OutreachGeneratorProps {
  contactId: number;
  contactName: string;
  company: string;
  title: string;
  icpScore?: number;
  matchReasons?: string[];
}

interface GeneratedOutreach {
  subject?: string;
  opening?: string;
  body: string;
  cta?: string;
  signature_note?: string;
  message?: string;
}

interface CallScript {
  opener: string;
  permission_ask: string;
  value_statement: string;
  discovery_questions: string[];
  talking_points: string[];
  objection_handlers: Record<string, string>;
  meeting_ask: string;
  voicemail_script: string;
}

interface SequenceEmail {
  subject: string;
  body: string;
  cta: string;
  send_day: string;
}

type Template = 'intro' | 'follow_up' | 'value_add' | 'meeting_request' | 'referral' | 'event';
type Tone = 'professional' | 'casual' | 'executive' | 'challenger';
type Channel = 'email' | 'linkedin' | 'call';
type CallType = 'discovery' | 'follow_up' | 'demo_set' | 'check_in';

const TEMPLATES: { id: Template; label: string; icon: React.ReactNode; description: string }[] = [
  { id: 'intro', label: 'Introduction', icon: <Zap size={16} />, description: 'First touch, build interest' },
  { id: 'follow_up', label: 'Follow-up', icon: <RefreshCw size={16} />, description: 'Continue the conversation' },
  { id: 'value_add', label: 'Value Add', icon: <Sparkles size={16} />, description: 'Share insight or resource' },
  { id: 'meeting_request', label: 'Meeting Request', icon: <Clock size={16} />, description: 'Ask for time directly' },
  { id: 'referral', label: 'Referral Ask', icon: <Target size={16} />, description: 'Request an introduction' },
  { id: 'event', label: 'Event-Based', icon: <Zap size={16} />, description: 'Triggered by news/event' },
];

const TONES: { id: Tone; label: string; description: string }[] = [
  { id: 'professional', label: 'Professional', description: 'Polished & credible' },
  { id: 'casual', label: 'Casual', description: 'Friendly & approachable' },
  { id: 'executive', label: 'Executive', description: 'Concise & high-level' },
  { id: 'challenger', label: 'Challenger', description: 'Thought-provoking' },
];

const CALL_TYPES: { id: CallType; label: string; description: string }[] = [
  { id: 'discovery', label: 'Discovery Call', description: 'First conversation, uncover needs' },
  { id: 'follow_up', label: 'Follow-up Call', description: 'Continue previous conversation' },
  { id: 'demo_set', label: 'Demo/Meeting Set', description: 'Book a formal meeting' },
  { id: 'check_in', label: 'Check-in', description: 'Nurture existing relationship' },
];

const OBJECTION_LABELS: Record<string, { label: string; icon: React.ReactNode }> = {
  'no_time': { label: "No Time", icon: <Clock size={14} /> },
  'not_interested': { label: "Not Interested", icon: <Shield size={14} /> },
  'send_info': { label: "Send Info", icon: <Mail size={14} /> },
  'have_solution': { label: "Have Solution", icon: <Check size={14} /> },
  'no_budget': { label: "No Budget", icon: <AlertCircle size={14} /> },
};

export default function OutreachGenerator({
  contactId,
  contactName,
  company,
  title,
  icpScore,
  matchReasons = []
}: OutreachGeneratorProps) {
  const [channel, setChannel] = useState<Channel>('email');
  const [template, setTemplate] = useState<Template>('intro');
  const [tone, setTone] = useState<Tone>('professional');
  const [callType, setCallType] = useState<CallType>('discovery');
  const [customContext, setCustomContext] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const [generating, setGenerating] = useState(false);
  const [outreach, setOutreach] = useState<GeneratedOutreach | null>(null);
  const [callScript, setCallScript] = useState<CallScript | null>(null);
  const [copied, setCopied] = useState(false);
  const [copiedItem, setCopiedItem] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const [showSequence, setShowSequence] = useState(false);
  const [generatingSequence, setGeneratingSequence] = useState(false);
  const [sequence, setSequence] = useState<SequenceEmail[]>([]);
  const [activeSequenceIdx, setActiveSequenceIdx] = useState(0);
  
  // Call script UI state
  const [expandedObjection, setExpandedObjection] = useState<string | null>(null);

  const generateOutreach = async () => {
    setGenerating(true);
    setError(null);
    setOutreach(null);
    setCallScript(null);
    
    try {
      if (channel === 'call') {
        // Generate call script
        const res = await fetch(`http://localhost:8000/api/contacts/${contactId}/generate-call-script`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ call_type: callType })
        });
        
        const data = await res.json();
        
        if (data.success && data.script) {
          setCallScript(data.script);
        } else {
          setError(data.error || 'Failed to generate call script');
        }
      } else {
        // Generate email/LinkedIn
        const res = await fetch(`http://localhost:8000/api/contacts/${contactId}/generate-outreach`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ template, tone, channel, context: customContext })
        });
        
        const data = await res.json();
        
        if (data.success && data.outreach) {
          setOutreach(data.outreach);
        } else {
          setError(data.error || 'Failed to generate outreach');
        }
      }
    } catch (e) {
      setError('Failed to connect to server');
    } finally {
      setGenerating(false);
    }
  };

  const generateSequence = async () => {
    setGeneratingSequence(true);
    setSequence([]);
    
    try {
      const res = await fetch(`http://localhost:8000/api/contacts/${contactId}/generate-sequence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tone })
      });
      
      const data = await res.json();
      
      if (data.success && data.sequence) {
        setSequence(data.sequence);
        setShowSequence(true);
        setActiveSequenceIdx(0);
      }
    } catch (e) {
      console.error('Sequence generation failed:', e);
    } finally {
      setGeneratingSequence(false);
    }
  };

  const copyToClipboard = async (text: string, itemId?: string) => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    if (itemId) setCopiedItem(itemId);
    setTimeout(() => {
      setCopied(false);
      setCopiedItem(null);
    }, 2000);
  };

  const getFullEmailText = () => {
    if (!outreach) return '';
    if (channel === 'linkedin') {
      return outreach.message || outreach.body;
    }
    return [
      outreach.opening,
      '',
      outreach.body,
      '',
      outreach.cta,
      '',
      outreach.signature_note
    ].filter(Boolean).join('\n');
  };

  const getFullCallScript = () => {
    if (!callScript) return '';
    return `OPENER:\n${callScript.opener}\n\nPERMISSION:\n${callScript.permission_ask}\n\nVALUE STATEMENT:\n${callScript.value_statement}\n\nDISCOVERY QUESTIONS:\n${callScript.discovery_questions.map((q, i) => `${i + 1}. ${q}`).join('\n')}\n\nTALKING POINTS:\n${callScript.talking_points.map((p, i) => `• ${p}`).join('\n')}\n\nMEETING ASK:\n${callScript.meeting_ask}\n\nVOICEMAIL:\n${callScript.voicemail_script}`;
  };

  return (
    <div className="space-y-6">
      {/* ICP Score Banner */}
      {icpScore && icpScore > 0 && (
        <div className={`rounded-xl p-4 border ${
          icpScore >= 70 
            ? 'bg-gradient-to-r from-emerald-500/10 to-green-500/10 border-emerald-500/30' 
            : 'bg-gradient-to-r from-blue-500/10 to-indigo-500/10 border-blue-500/30'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold ${
                icpScore >= 70 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400'
              }`}>
                {icpScore}%
              </div>
              <div>
                <p className="text-white font-medium">ICP Match Score</p>
                <p className="text-sm text-[#8b919a]">
                  {matchReasons.slice(0, 2).join(' • ')}
                </p>
              </div>
            </div>
            <ThumbsUp size={20} className={icpScore >= 70 ? 'text-emerald-400' : 'text-blue-400'} />
          </div>
        </div>
      )}

      {/* Triple Channel Toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => { setChannel('email'); setOutreach(null); setCallScript(null); }}
          className={`flex-1 py-3 rounded-xl font-medium flex items-center justify-center gap-2 transition-all ${
            channel === 'email'
              ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/25'
              : 'bg-[#21262d] text-[#8b919a] hover:text-white'
          }`}
        >
          <Mail size={18} />
          Email
        </button>
        <button
          onClick={() => { setChannel('call'); setOutreach(null); setCallScript(null); }}
          className={`flex-1 py-3 rounded-xl font-medium flex items-center justify-center gap-2 transition-all ${
            channel === 'call'
              ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg shadow-emerald-500/25'
              : 'bg-[#21262d] text-[#8b919a] hover:text-white'
          }`}
        >
          <Phone size={18} />
          Call
        </button>
        <button
          onClick={() => { setChannel('linkedin'); setOutreach(null); setCallScript(null); }}
          className={`flex-1 py-3 rounded-xl font-medium flex items-center justify-center gap-2 transition-all ${
            channel === 'linkedin'
              ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/25'
              : 'bg-[#21262d] text-[#8b919a] hover:text-white'
          }`}
        >
          <Linkedin size={18} />
          LinkedIn
        </button>
      </div>

      {/* Channel-specific options */}
      {channel === 'call' ? (
        /* Call Type Selection */
        <div>
          <label className="block text-sm text-[#8b919a] mb-2">Call Type</label>
          <div className="grid grid-cols-2 gap-2">
            {CALL_TYPES.map(t => (
              <button
                key={t.id}
                onClick={() => setCallType(t.id)}
                className={`p-3 rounded-lg text-left transition-all ${
                  callType === t.id
                    ? 'bg-emerald-600/20 border border-emerald-500/50 text-white'
                    : 'bg-[#21262d] border border-transparent text-[#8b919a] hover:text-white hover:border-[#30363d]'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <PhoneCall size={16} className={callType === t.id ? 'text-emerald-400' : ''} />
                  <span className="text-sm font-medium">{t.label}</span>
                </div>
                <p className="text-xs opacity-60">{t.description}</p>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <>
          {/* Template Selection (Email/LinkedIn) */}
          <div>
            <label className="block text-sm text-[#8b919a] mb-2">Message Type</label>
            <div className="grid grid-cols-3 gap-2">
              {TEMPLATES.map(t => (
                <button
                  key={t.id}
                  onClick={() => setTemplate(t.id)}
                  className={`p-3 rounded-lg text-left transition-all ${
                    template === t.id
                      ? 'bg-indigo-600/20 border border-indigo-500/50 text-white'
                      : 'bg-[#21262d] border border-transparent text-[#8b919a] hover:text-white hover:border-[#30363d]'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className={template === t.id ? 'text-indigo-400' : ''}>{t.icon}</span>
                    <span className="text-sm font-medium">{t.label}</span>
                  </div>
                  <p className="text-xs opacity-60">{t.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Tone Selection */}
          <div>
            <label className="block text-sm text-[#8b919a] mb-2">Tone</label>
            <div className="flex gap-2">
              {TONES.map(t => (
                <button
                  key={t.id}
                  onClick={() => setTone(t.id)}
                  className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                    tone === t.id
                      ? 'bg-purple-600/20 border border-purple-500/50 text-purple-300'
                      : 'bg-[#21262d] text-[#8b919a] hover:text-white'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Advanced Options */}
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="flex items-center gap-2 text-sm text-[#8b919a] hover:text-white"
      >
        <Settings size={14} />
        Advanced Options
        <ChevronDown size={14} className={`transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
      </button>

      {showAdvanced && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <label className="block text-sm text-[#8b919a] mb-2">Custom Context (optional)</label>
          <textarea
            value={customContext}
            onChange={(e) => setCustomContext(e.target.value)}
            placeholder="Add specific details: recent news, mutual connection, event trigger, specific pain points..."
            className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-3 text-white placeholder-[#6e7681] focus:outline-none focus:border-indigo-500 resize-none"
            rows={2}
          />
        </div>
      )}

      {/* Generate Buttons */}
      <div className="flex gap-3">
        <button
          onClick={generateOutreach}
          disabled={generating}
          className={`flex-1 py-3 rounded-xl font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all ${
            channel === 'call'
              ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500'
              : channel === 'linkedin'
              ? 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500'
              : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500'
          }`}
        >
          {generating ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              {channel === 'call' ? 'Building Script...' : 'Crafting Message...'}
            </>
          ) : (
            <>
              <Wand2 size={18} />
              Generate {channel === 'call' ? 'Call Script' : channel === 'linkedin' ? 'Message' : 'Email'}
            </>
          )}
        </button>
        
        {channel === 'email' && (
          <button
            onClick={generateSequence}
            disabled={generatingSequence}
            className="py-3 px-4 bg-[#21262d] hover:bg-[#30363d] rounded-xl font-medium flex items-center gap-2 disabled:opacity-50"
            title="Generate 3-email sequence"
          >
            {generatingSequence ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Layers size={18} />
            )}
          </button>
        )}
      </div>

      {/* Error Display */}
      {error && (
