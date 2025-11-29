import React, { useState } from 'react';
import { Mail, Phone, MessageSquare, Copy, Check, Sparkles, RefreshCw, Loader, ChevronRight } from 'lucide-react';
import "../styles/ContentGenerator.css";


interface ContentGeneratorProps {
  contactId: number;
  contactName: string;
  profileContent?: string;
}

interface EmailContent {
  subject: string;
  body: string;
  generatedat: string;
}

interface CallScriptContent {
  script: string;
  generatedat: string;
}

interface LinkedInContent {
  message: string;
  generatedat: string;
}

interface GeneratedContent {
  emails?: EmailContent[];
  call_scripts?: CallScriptContent[];
  linkedin_messages?: LinkedInContent[];
}

export default function ContentGenerator({ contactId, contactName, profileContent }: ContentGeneratorProps) {
  const [activeType, setActiveType] = useState<'email' | 'call' | 'linkedin'>('email');
  const [activeIndex, setActiveIndex] = useState(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [content, setContent] = useState<GeneratedContent | null>(null);
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generateContent = async (type: 'email' | 'call' | 'linkedin' | 'all' = 'all') => {
    if (!profileContent) {
      setError('Contact must be enriched first');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch(`https://apex-intelligence-production.up.railway.app/api/contacts/${contactId}/generate-content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ type }),
      });

      const data = await response.json();

      if (data.success && data.results) {
        setContent(data.results);
        setActiveIndex(0); // Reset to first item
      } else {
        setError(data.error || 'Failed to generate content');
      }
    } catch (err) {
      setError('Network error - is the backend running?');
      console.error('Content generation error:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = async (text: string, field: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const getCurrentContent = () => {
    if (!content) return null;

    if (activeType === 'email' && content.emails) {
      return content.emails[activeIndex];
    } else if (activeType === 'call' && content.call_scripts) {
      return content.call_scripts[activeIndex];
    } else if (activeType === 'linkedin' && content.linkedin_messages) {
      return content.linkedin_messages[activeIndex];
    }
    return null;
  };

  const getMaxIndex = () => {
    if (!content) return 0;
    if (activeType === 'email') return (content.emails?.length || 1) - 1;
    if (activeType === 'call') return (content.call_scripts?.length || 1) - 1;
    if (activeType === 'linkedin') return (content.linkedin_messages?.length || 1) - 1;
    return 0;
  };

  const renderEmailContent = () => {
    const email = getCurrentContent() as EmailContent;
    if (!email) return null;

    const maxIndex = getMaxIndex();

    return (
      <div className="content-display">
        <div className="content-header">
          <div className="header-left">
            <h3>📧 Email {activeIndex + 1} of {maxIndex + 1}</h3>
            <span className="email-label">
              {activeIndex === 0 ? 'Introduction' : activeIndex === 1 ? 'Value Add' : 'Follow-up'}
            </span>
          </div>
          <button 
            className="copy-all-btn"
            onClick={() => copyToClipboard(
              `Subject: ${email.subject}\n\n${email.body}`,
              `email-${activeIndex}-full`
            )}
          >
            {copiedField === `email-${activeIndex}-full` ? <Check size={16} /> : <Copy size={16} />}
            Copy All
          </button>
        </div>

        {maxIndex > 0 && (
          <div className="sequence-nav">
            {Array.from({ length: maxIndex + 1 }, (_, i) => (
              <button
                key={i}
                className={`sequence-btn ${activeIndex === i ? 'active' : ''}`}
                onClick={() => setActiveIndex(i)}
              >
                Email {i + 1}
              </button>
            ))}
          </div>
        )}

        <div className="email-subject">
          <label>Subject Line</label>
          <div className="copy-group">
            <input 
              type="text" 
              value={email.subject} 
              readOnly 
            />
            <button 
              className="mini-copy-btn"
              onClick={() => copyToClipboard(email.subject, `email-${activeIndex}-subject`)}
            >
              {copiedField === `email-${activeIndex}-subject` ? <Check size={14} /> : <Copy size={14} />}
            </button>
          </div>
        </div>

        <div className="email-body">
          <label>Email Body</label>
          <div className="copy-group">
            <textarea 
              value={email.body} 
              readOnly 
              rows={12}
            />
            <button 
              className="mini-copy-btn"
              onClick={() => copyToClipboard(email.body, `email-${activeIndex}-body`)}
            >
              {copiedField === `email-${activeIndex}-body` ? <Check size={14} /> : <Copy size={14} />}
            </button>
          </div>
        </div>

        <div className="content-meta">
          Generated {new Date(email.generatedat).toLocaleString()}
        </div>
      </div>
    );
  };

  const renderCallScriptContent = () => {
    const script = getCurrentContent() as CallScriptContent;
    if (!script) return null;

    const maxIndex = getMaxIndex();

    return (
      <div className="content-display">
        <div className="content-header">
          <div className="header-left">
            <h3>📞 Call Script {activeIndex + 1} of {maxIndex + 1}</h3>
            <span className="email-label">
              {activeIndex === 0 ? 'Cold Call' : activeIndex === 1 ? 'Follow-up' : 'Executive Briefing'}
            </span>
          </div>
          <button 
            className="copy-all-btn"
            onClick={() => copyToClipboard(script.script, `call-${activeIndex}-script`)}
          >
            {copiedField === `call-${activeIndex}-script` ? <Check size={16} /> : <Copy size={16} />}
            Copy All
          </button>
        </div>

        {maxIndex > 0 && (
          <div className="sequence-nav">
            {Array.from({ length: maxIndex + 1 }, (_, i) => (
              <button
                key={i}
                className={`sequence-btn ${activeIndex === i ? 'active' : ''}`}
                onClick={() => setActiveIndex(i)}
              >
                Script {i + 1}
              </button>
            ))}
          </div>
        )}

        <div className="script-content">
          <pre>{script.script}</pre>
        </div>

        <div className="content-meta">
          Generated {new Date(script.generatedat).toLocaleString()}
        </div>
      </div>
    );
  };

  const renderLinkedInContent = () => {
    const message = getCurrentContent() as LinkedInContent;
    if (!message) return null;

    const maxIndex = getMaxIndex();

    return (
      <div className="content-display">
        <div className="content-header">
          <div className="header-left">
            <h3>💼 LinkedIn {activeIndex + 1} of {maxIndex + 1}</h3>
            <span className="email-label">
              {activeIndex === 0 ? 'Connection Request' : 'Follow-up Message'}
            </span>
          </div>
          <button 
            className="copy-all-btn"
            onClick={() => copyToClipboard(message.message, `linkedin-${activeIndex}-msg`)}
          >
            {copiedField === `linkedin-${activeIndex}-msg` ? <Check size={16} /> : <Copy size={16} />}
            Copy
          </button>
        </div>

        {maxIndex > 0 && (
          <div className="sequence-nav">
            {Array.from({ length: maxIndex + 1 }, (_, i) => (
              <button
                key={i}
                className={`sequence-btn ${activeIndex === i ? 'active' : ''}`}
                onClick={() => setActiveIndex(i)}
              >
                Message {i + 1}
              </button>
            ))}
          </div>
        )}

        <div className="linkedin-message">
          <textarea 
            value={message.message} 
            readOnly 
            rows={6}
          />
          <div className="char-count">
            {message.message.length} characters
            {activeIndex === 0 && message.message.length > 300 && (
              <span className="warning"> (LinkedIn limit: 300)</span>
            )}
          </div>
        </div>

        <div className="content-meta">
          Generated {new Date(message.generatedat).toLocaleString()}
        </div>
      </div>
    );
  };

  if (!profileContent) {
    return (
      <div className="content-generator-empty">
        <Sparkles size={48} />
        <p>Contact needs to be enriched first</p>
        <p className="hint">Click "Enrich Contact" button to generate AI intelligence</p>
      </div>
    );
  }

  return (
    <div className="content-generator">
      {/* Type Selector Tabs */}
      <div className="content-type-tabs">
        <button
          className={`content-tab ${activeType === 'email' ? 'active' : ''}`}
          onClick={() => { setActiveType('email'); setActiveIndex(0); }}
        >
          <Mail size={16} />
          Email Sequence
          {content?.emails && <span className="count">{content.emails.length}</span>}
        </button>
        <button
          className={`content-tab ${activeType === 'call' ? 'active' : ''}`}
          onClick={() => { setActiveType('call'); setActiveIndex(0); }}
        >
          <Phone size={16} />
          Call Scripts
          {content?.call_scripts && <span className="count">{content.call_scripts.length}</span>}
        </button>
        <button
          className={`content-tab ${activeType === 'linkedin' ? 'active' : ''}`}
          onClick={() => { setActiveType('linkedin'); setActiveIndex(0); }}
        >
          <MessageSquare size={16} />
          LinkedIn
          {content?.linkedin_messages && <span className="count">{content.linkedin_messages.length}</span>}
        </button>
      </div>

      {/* Generate Button */}
      {!content && (
        <div className="generate-section">
          <button 
            className="generate-btn"
            onClick={() => generateContent('all')}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <Loader size={18} className="spin" />
                Generating AI Content...
              </>
            ) : (
              <>
                <Sparkles size={18} />
                Generate All Content
              </>
            )}
          </button>
          <p className="generate-hint">
            Creates 3 personalized emails, 3 call scripts, and 2 LinkedIn messages using AI intelligence
          </p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="content-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Content Display */}
      {content && (
        <>
          <div className="regenerate-section">
            <button 
              className="regenerate-btn"
              onClick={() => generateContent(activeType)}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <Loader size={16} className="spin" />
                  Regenerating...
                </>
              ) : (
                <>
                  <RefreshCw size={16} />
                  Regenerate {activeType === 'email' ? 'Emails' : activeType === 'call' ? 'Scripts' : 'LinkedIn'}
                </>
              )}
            </button>
          </div>

          {activeType === 'email' && renderEmailContent()}
          {activeType === 'call' && renderCallScriptContent()}
          {activeType === 'linkedin' && renderLinkedInContent()}
        </>
      )}
    </div>
  );
}