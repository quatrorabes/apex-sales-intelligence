// =============================================================================
// OutreachGenerator.tsx - Triple-Channel AI Outreach Suite
// =============================================================================

import { useState } from 'react';
import {
  Mail, Sparkles, Copy, RefreshCw, Check,
  Send, Zap, Target, Brain, ChevronDown, Linkedin, Phone,
  Clock, FileText, Loader2, Settings, ThumbsUp, AlertCircle, 
  Wand2, Layers, Shield, PhoneCall, Voicemail
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

const TEMPLATES = [
  { id: 'intro' as Template, label: 'Introduction', icon: <Zap size={16} />, description: 'First touch' },
  { id: 'follow_up' as Template, label: 'Follow-up', icon: <RefreshCw size={16} />, description: 'Continue conversation' },
  { id: 'value_add' as Template, label: 'Value Add', icon: <Sparkles size={16} />, description: 'Share insight' },
  { id: 'meeting_request' as Template, label: 'Meeting', icon: <Clock size={16} />, description: 'Ask for time' },
  { id: 'referral' as Template, label: 'Referral', icon: <Target size={16} />, description: 'Get intro' },
  { id: 'event' as Template, label: 'Event', icon: <Zap size={16} />, description: 'News trigger' },
];

const TONES = [
  { id: 'professional' as Tone, label: 'Professional' },
  { id: 'casual' as Tone, label: 'Casual' },
  { id: 'executive' as Tone, label: 'Executive' },
  { id: 'challenger' as Tone, label: 'Challenger' },
];

const CALL_TYPES = [
  { id: 'discovery' as CallType, label: 'Discovery', description: 'Uncover needs' },
  { id: 'follow_up' as CallType, label: 'Follow-up', description: 'Continue conversation' },
  { id: 'demo_set' as CallType, label: 'Demo Set', description: 'Book meeting' },
  { id: 'check_in' as CallType, label: 'Check-in', description: 'Nurture' },
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
  const [expandedObjection, setExpandedObjection] = useState<string | null>(null);

  const generateOutreach = async () => {
    setGenerating(true);
    setError(null);
    setOutreach(null);
    setCallScript(null);
    
    try {
      if (channel === 'call') {
        const res = await fetch(`https://apex-backend-production-production.up.railway.app/api/contacts/${contactId}/generate-call-script`, {
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
        const res = await fetch(`https://apex-backend-production-production.up.railway.app/api/contacts/${contactId}/generate-outreach`, {
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
      const res = await fetch(`https://apex-backend-production-production.up.railway.app/api/contacts/${contactId}/generate-sequence`, {
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
    setTimeout(() => { setCopied(false); setCopiedItem(null); }, 2000);
  };

  const getFullEmailText = () => {
    if (!outreach) return '';
    if (channel === 'linkedin') return outreach.message || outreach.body;
    return [outreach.opening, '', outreach.body, '', outreach.cta, '', outreach.signature_note].filter(Boolean).join('\n');
  };

  const getFullCallScript = () => {
    if (!callScript) return '';
    return `OPENER:\n${callScript.opener}\n\nPERMISSION:\n${callScript.permission_ask}\n\nVALUE STATEMENT:\n${callScript.value_statement}\n\nDISCOVERY QUESTIONS:\n${callScript.discovery_questions.map((q, i) => `${i + 1}. ${q}`).join('\n')}\n\nTALKING POINTS:\n${callScript.talking_points.map(p => `• ${p}`).join('\n')}\n\nMEETING ASK:\n${callScript.meeting_ask}\n\nVOICEMAIL:\n${callScript.voicemail_script}`;
  };

  return (
    <div className="space-y-6">
      {/* ICP Score Banner */}
      {icpScore && icpScore > 0 && (
        <div className={`rounded-xl p-4 border ${icpScore >= 70 ? 'bg-gradient-to-r from-emerald-500/10 to-green-500/10 border-emerald-500/30' : 'bg-gradient-to-r from-blue-500/10 to-indigo-500/10 border-blue-500/30'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold ${icpScore >= 70 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400'}`}>
                {icpScore}%
              </div>
              <div>
                <p className="text-white font-medium">ICP Match Score</p>
                <p className="text-sm text-[#8b919a]">{matchReasons.slice(0, 2).join(' • ')}</p>
              </div>
            </div>
            <ThumbsUp size={20} className={icpScore >= 70 ? 'text-emerald-400' : 'text-blue-400'} />
          </div>
        </div>
      )}

      {/* Triple Channel Toggle */}
      <div className="flex gap-2">
        <button onClick={() => { setChannel('email'); setOutreach(null); setCallScript(null); }}
          className={`flex-1 py-3 rounded-xl font-medium flex items-center justify-center gap-2 transition-all ${channel === 'email' ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/25' : 'bg-[#21262d] text-[#8b919a] hover:text-white'}`}>
          <Mail size={18} /> Email
        </button>
        <button onClick={() => { setChannel('call'); setOutreach(null); setCallScript(null); }}
          className={`flex-1 py-3 rounded-xl font-medium flex items-center justify-center gap-2 transition-all ${channel === 'call' ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg shadow-emerald-500/25' : 'bg-[#21262d] text-[#8b919a] hover:text-white'}`}>
          <Phone size={18} /> Call
        </button>
        <button onClick={() => { setChannel('linkedin'); setOutreach(null); setCallScript(null); }}
          className={`flex-1 py-3 rounded-xl font-medium flex items-center justify-center gap-2 transition-all ${channel === 'linkedin' ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/25' : 'bg-[#21262d] text-[#8b919a] hover:text-white'}`}>
          <Linkedin size={18} /> LinkedIn
        </button>
      </div>

      {/* Channel-specific options */}
      {channel === 'call' ? (
        <div>
          <label className="block text-sm text-[#8b919a] mb-2">Call Type</label>
          <div className="grid grid-cols-2 gap-2">
            {CALL_TYPES.map(t => (
              <button key={t.id} onClick={() => setCallType(t.id)}
                className={`p-3 rounded-lg text-left transition-all ${callType === t.id ? 'bg-emerald-600/20 border border-emerald-500/50 text-white' : 'bg-[#21262d] border border-transparent text-[#8b919a] hover:text-white'}`}>
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
          <div>
            <label className="block text-sm text-[#8b919a] mb-2">Message Type</label>
            <div className="grid grid-cols-3 gap-2">
              {TEMPLATES.map(t => (
                <button key={t.id} onClick={() => setTemplate(t.id)}
                  className={`p-3 rounded-lg text-left transition-all ${template === t.id ? 'bg-indigo-600/20 border border-indigo-500/50 text-white' : 'bg-[#21262d] border border-transparent text-[#8b919a] hover:text-white'}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={template === t.id ? 'text-indigo-400' : ''}>{t.icon}</span>
                    <span className="text-sm font-medium">{t.label}</span>
                  </div>
                  <p className="text-xs opacity-60">{t.description}</p>
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm text-[#8b919a] mb-2">Tone</label>
            <div className="flex gap-2">
              {TONES.map(t => (
                <button key={t.id} onClick={() => setTone(t.id)}
                  className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${tone === t.id ? 'bg-purple-600/20 border border-purple-500/50 text-purple-300' : 'bg-[#21262d] text-[#8b919a] hover:text-white'}`}>
                  {t.label}
                </button>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Advanced Options */}
      <button onClick={() => setShowAdvanced(!showAdvanced)} className="flex items-center gap-2 text-sm text-[#8b919a] hover:text-white">
        <Settings size={14} /> Advanced Options
        <ChevronDown size={14} className={`transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
      </button>

      {showAdvanced && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <label className="block text-sm text-[#8b919a] mb-2">Custom Context</label>
          <textarea value={customContext} onChange={(e) => setCustomContext(e.target.value)}
            placeholder="Recent news, mutual connection, specific pain points..."
            className="w-full bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-3 text-white placeholder-[#6e7681] focus:outline-none focus:border-indigo-500 resize-none" rows={2} />
        </div>
      )}

      {/* Generate Buttons */}
      <div className="flex gap-3">
        <button onClick={generateOutreach} disabled={generating}
          className={`flex-1 py-3 rounded-xl font-medium flex items-center justify-center gap-2 disabled:opacity-50 ${channel === 'call' ? 'bg-gradient-to-r from-emerald-600 to-teal-600' : channel === 'linkedin' ? 'bg-gradient-to-r from-blue-600 to-cyan-600' : 'bg-gradient-to-r from-indigo-600 to-purple-600'}`}>
          {generating ? <><Loader2 size={18} className="animate-spin" /> Generating...</> : <><Wand2 size={18} /> Generate {channel === 'call' ? 'Script' : channel === 'linkedin' ? 'Message' : 'Email'}</>}
        </button>
        {channel === 'email' && (
          <button onClick={generateSequence} disabled={generatingSequence}
            className="py-3 px-4 bg-[#21262d] hover:bg-[#30363d] rounded-xl font-medium flex items-center gap-2 disabled:opacity-50" title="Generate 3-email sequence">
            {generatingSequence ? <Loader2 size={18} className="animate-spin" /> : <Layers size={18} />}
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle size={20} className="text-red-400" />
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* Email/LinkedIn Output */}
      {outreach && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl overflow-hidden">
          <div className="px-5 py-4 border-b border-[#30363d] flex items-center justify-between bg-gradient-to-r from-indigo-600/10 to-purple-600/10">
            <div className="flex items-center gap-3">
              <Sparkles size={18} className="text-indigo-400" />
              <span className="text-white font-medium">Generated {channel === 'email' ? 'Email' : 'Message'}</span>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={generateOutreach} className="p-2 hover:bg-[#21262d] rounded-lg text-[#8b919a] hover:text-white"><RefreshCw size={16} /></button>
              <button onClick={() => copyToClipboard(getFullEmailText())}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-1.5 ${copied ? 'bg-emerald-600' : 'bg-indigo-600 hover:bg-indigo-500'}`}>
                {copied ? <><Check size={14} /> Copied!</> : <><Copy size={14} /> Copy</>}
              </button>
            </div>
          </div>
          <div className="p-5">
            {channel === 'email' && outreach.subject && (
              <div className="mb-4">
                <label className="block text-xs text-[#6e7681] mb-1">Subject</label>
                <div className="bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-white font-medium">{outreach.subject}</div>
              </div>
            )}
            <div className="space-y-3 text-[#b8bcc4]">
              {outreach.opening && <p className="text-white">{outreach.opening}</p>}
              <p>{outreach.body}</p>
              {outreach.cta && <p className="text-indigo-300">{outreach.cta}</p>}
              {outreach.signature_note && <p className="text-[#8b919a] italic">{outreach.signature_note}</p>}
            </div>
          </div>
          <div className="px-5 py-3 border-t border-[#30363d] bg-[#0d1117] flex items-center gap-3">
            <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-medium flex items-center gap-2">
              <Send size={14} /> Open in {channel === 'email' ? 'Gmail' : 'LinkedIn'}
            </button>
          </div>
        </div>
      )}

      {/* Call Script Output */}
      {callScript && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl overflow-hidden">
          <div className="px-5 py-4 border-b border-[#30363d] flex items-center justify-between bg-gradient-to-r from-emerald-600/10 to-teal-600/10">
            <div className="flex items-center gap-3">
              <Phone size={18} className="text-emerald-400" />
              <span className="text-white font-medium">Call Script</span>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={generateOutreach} className="p-2 hover:bg-[#21262d] rounded-lg text-[#8b919a] hover:text-white"><RefreshCw size={16} /></button>
              <button onClick={() => copyToClipboard(getFullCallScript())}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-1.5 ${copied && !copiedItem ? 'bg-emerald-600' : 'bg-emerald-600 hover:bg-emerald-500'}`}>
                {copied && !copiedItem ? <><Check size={14} /> Copied!</> : <><Copy size={14} /> Copy All</>}
              </button>
            </div>
          </div>
          
          <div className="p-5 space-y-5">
            {/* Opener */}
            <div className="bg-[#0d1117] rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-emerald-400 uppercase tracking-wide">Opener</span>
                <button onClick={() => copyToClipboard(callScript.opener, 'opener')} className="text-[#6e7681] hover:text-white">
                  {copiedItem === 'opener' ? <Check size={14} /> : <Copy size={14} />}
                </button>
              </div>
              <p className="text-white">{callScript.opener}</p>
            </div>

            {/* Permission */}
            <div className="bg-[#0d1117] rounded-lg p-4">
              <span className="text-xs font-medium text-blue-400 uppercase tracking-wide">Permission Ask</span>
              <p className="text-[#b8bcc4] mt-2">{callScript.permission_ask}</p>
            </div>

            {/* Value Statement */}
            <div className="bg-[#0d1117] rounded-lg p-4">
              <span className="text-xs font-medium text-purple-400 uppercase tracking-wide">Value Statement</span>
              <p className="text-[#b8bcc4] mt-2">{callScript.value_statement}</p>
            </div>
            {/* Discovery Questions */}
            <div className="bg-[#0d1117] rounded-lg p-4">
              <span className="text-xs font-medium text-yellow-400 uppercase tracking-wide">Discovery Questions</span>
              <ol className="mt-3 space-y-2">
                {callScript.discovery_questions.map((q, i) => (
                  <li key={i} className="flex gap-3 text-[#b8bcc4]">
                    <span className="text-yellow-400 font-mono text-sm">{i + 1}.</span>
                    <span>{q}</span>
                  </li>
                ))}
              </ol>
            </div>

            {/* Talking Points */}
            <div className="bg-[#0d1117] rounded-lg p-4">
              <span className="text-xs font-medium text-cyan-400 uppercase tracking-wide">Talking Points</span>
              <ul className="mt-3 space-y-2">
                {callScript.talking_points.map((p, i) => (
                  <li key={i} className="flex gap-3 text-[#b8bcc4]">
                    <span className="text-cyan-400">•</span>
                    <span>{p}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Objection Handlers */}
            <div className="bg-[#0d1117] rounded-lg p-4">
              <span className="text-xs font-medium text-red-400 uppercase tracking-wide">Objection Handlers</span>
              <div className="mt-3 space-y-2">
                {Object.entries(callScript.objection_handlers).map(([key, response]) => (
                  <div key={key} className="border border-[#30363d] rounded-lg overflow-hidden">
                    <button
                      onClick={() => setExpandedObjection(expandedObjection === key ? null : key)}
                      className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-[#161b22] transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        {OBJECTION_LABELS[key]?.icon || <Shield size={14} />}
                        <span className="text-white font-medium text-sm">{OBJECTION_LABELS[key]?.label || key}</span>
                      </div>
                      <ChevronDown size={16} className={`text-[#6e7681] transition-transform ${expandedObjection === key ? 'rotate-180' : ''}`} />
                    </button>
                    {expandedObjection === key && (
                      <div className="px-4 py-3 border-t border-[#30363d] bg-[#161b22]">
                        <p className="text-[#b8bcc4] text-sm">{response}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Meeting Ask */}
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-4">
              <span className="text-xs font-medium text-emerald-400 uppercase tracking-wide">Meeting Ask (Close)</span>
              <p className="text-white mt-2 font-medium">{callScript.meeting_ask}</p>
            </div>

            {/* Voicemail */}
            <div className="bg-[#0d1117] rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Voicemail size={16} className="text-orange-400" />
                  <span className="text-xs font-medium text-orange-400 uppercase tracking-wide">Voicemail Script</span>
                </div>
                <button onClick={() => copyToClipboard(callScript.voicemail_script, 'voicemail')} className="text-[#6e7681] hover:text-white">
                  {copiedItem === 'voicemail' ? <Check size={14} /> : <Copy size={14} />}
                </button>
              </div>
              <p className="text-[#b8bcc4]">{callScript.voicemail_script}</p>
            </div>
          </div>
        </div>
      )}

      {/* Email Sequence */}
      {showSequence && sequence.length > 0 && (
        <div className="bg-[#161b22] border border-[#30363d] rounded-xl overflow-hidden">
          <div className="px-5 py-4 border-b border-[#30363d] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Layers size={18} className="text-purple-400" />
              <span className="text-white font-medium">3-Email Sequence</span>
            </div>
            <button onClick={() => setShowSequence(false)} className="text-[#8b919a] hover:text-white text-sm">Hide</button>
          </div>
          
          <div className="flex border-b border-[#30363d]">
            {sequence.map((email, idx) => (
              <button key={idx} onClick={() => setActiveSequenceIdx(idx)}
                className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 border-b-2 transition-all ${activeSequenceIdx === idx ? 'border-purple-500 text-white bg-purple-500/10' : 'border-transparent text-[#8b919a] hover:text-white'}`}>
                <span className={`w-5 h-5 rounded-full text-xs flex items-center justify-center ${activeSequenceIdx === idx ? 'bg-purple-500' : 'bg-[#30363d]'}`}>{idx + 1}</span>
                {email.send_day}
              </button>
            ))}
          </div>
          
          <div className="p-5">
            <div className="mb-4">
              <label className="block text-xs text-[#6e7681] mb-1">Subject</label>
              <div className="bg-[#0d1117] border border-[#30363d] rounded-lg px-4 py-2.5 text-white">{sequence[activeSequenceIdx]?.subject}</div>
            </div>
            <div className="space-y-3 text-[#b8bcc4]">
              <p>{sequence[activeSequenceIdx]?.body}</p>
              <p className="text-indigo-300">{sequence[activeSequenceIdx]?.cta}</p>
            </div>
          </div>
          
          <div className="px-5 py-3 border-t border-[#30363d] bg-[#0d1117]">
            <button onClick={() => {
              const allEmails = sequence.map((e, i) => `--- Email ${i + 1} (${e.send_day}) ---\nSubject: ${e.subject}\n\n${e.body}\n\n${e.cta}`).join('\n\n');
              copyToClipboard(allEmails);
            }} className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg text-sm font-medium flex items-center gap-2">
              <Copy size={14} /> Copy Full Sequence
            </button>
          </div>
        </div>
      )}

      {/* Tips */}
      {!outreach && !callScript && !generating && (
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Brain size={20} className="text-blue-400 mt-0.5" />
            <div>
              <p className="text-white font-medium text-sm mb-1">AI-Powered Personalization</p>
              <p className="text-[#8b919a] text-sm">
                {channel === 'call' 
                  ? `Call scripts include openers, discovery questions, objection handlers, and voicemail scripts tailored to ${contactName}.`
                  : `Messages are crafted using ${contactName}'s profile, your playbook value props, ICP match analysis, and personality insights.`
                }
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

          