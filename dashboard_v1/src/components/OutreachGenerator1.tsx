import React, { useState } from 'react';
import { Mail, Linkedin, Phone, Loader2, Copy, Check } from 'lucide-react';

interface OutreachGeneratorProps {
  contactId: string;
}

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'https://apex-backend-i7b0.onrender.com';

export function OutreachGenerator({ contactId }: OutreachGeneratorProps): JSX.Element {
  const [selectedType, setSelectedType] = useState<'email' | 'linkedin' | 'coldcall'>('email');
  const [generating, setGenerating] = useState(false);
  const [content, setContent] = useState<string>('');
  const [copied, setCopied] = useState(false);

  const generateContent = async () => {
    setGenerating(true);
    setContent('');
    
    try {
      const endpoint = selectedType === 'email' ? 'generate-email' : selectedType === 'linkedin' ? 'generate-linkedin' : 'generate-coldcall';
      const url = `${API_BASE}/api/v2/contacts/${contactId}/${endpoint}`;
      
      console.log('[APEX] Generating outreach:', url);
      const res = await fetch(url, { method: 'POST' });
      
      if (!res.ok) {
        console.error('[APEX] Outreach generation failed', res.status);
        setContent('Failed to generate content. Please try again.');
        return;
      }
      
      const data = await res.json();
      setContent(data.content || data.message || 'No content generated');
      
    } catch (err) {
      console.error('[APEX] Error generating outreach', err);
      setContent('Error generating content. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const buttonClass = (type: string) => {
    const isActive = selectedType === type;
    return [
      'flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors',
      isActive
        ? 'bg-sky-500/10 border-sky-500/30 text-sky-300'
        : 'border-slate-700 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
    ].join(' ');
  };

  return (
    <div className="max-w-4xl space-y-4">
      <div className="flex items-center gap-3">
        <button className={buttonClass('email')} onClick={() => setSelectedType('email')}>
          <Mail className="h-4 w-4" />
          Email
        </button>
        <button className={buttonClass('linkedin')} onClick={() => setSelectedType('linkedin')}>
          <Linkedin className="h-4 w-4" />
          LinkedIn
        </button>
        <button className={buttonClass('coldcall')} onClick={() => setSelectedType('coldcall')}>
          <Phone className="h-4 w-4" />
          Cold Call Script
        </button>
      </div>

      <button
        onClick={generateContent}
        disabled={generating}
        className="px-6 py-2.5 bg-sky-500 hover:bg-sky-600 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center gap-2"
      >
        {generating ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Generating...
          </>
        ) : (
          `Generate ${selectedType === 'email' ? 'Email' : selectedType === 'linkedin' ? 'LinkedIn Message' : 'Call Script'}`
        )}
      </button>

      {content && (
        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-200">Generated Content</h3>
            <button
              onClick={copyToClipboard}
              className="flex items-center gap-2 px-3 py-1.5 text-xs rounded-md border border-slate-700 text-slate-300 hover:bg-slate-800 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="h-3.5 w-3.5 text-emerald-400" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" />
                  Copy
                </>
              )}
            </button>
          </div>
          <div className="rounded-md bg-slate-900/80 p-4 border border-slate-700">
            <pre className="whitespace-pre-wrap text-sm text-slate-200 font-sans">{content}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
