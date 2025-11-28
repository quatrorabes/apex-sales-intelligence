import React, { useState, useEffect } from 'react';
import { 
  X, 
  Sparkles, 
  Loader, 
  Mail, 
  Phone, 
  Linkedin,
  Target,
  Lightbulb,
  PhoneCall,
  StickyNote,
  AlertCircle,
  Copy,
  Check,
  RefreshCw,
  Zap,
  Calendar
} from 'lucide-react';

interface Contact {
  id: number;
  name: string;
  email: string;
  phone: string;
  company: string;
  title: string;
  enrichment_status?: string;
  profile_content?: string;
  enrichment_data?: string;
  pain_points?: string;
  talking_points?: string;
  product_match?: string;
  match_reasoning?: string;
  recommended_action?: string;
  mdcp_score?: number;
  rss_score?: number;
  priority_score?: number;
  notes?: string;
  email_1_subject?: string;
  email_1_body?: string;
  email_2_subject?: string;
  email_2_body?: string;
  email_3_subject?: string;
  email_3_body?: string;
}

interface ContactDetailModalProps {
  contact: Contact;
  onClose: () => void;
  onEnrichmentComplete?: (contact: Contact) => void;
}

type ViewMode = 'intelligence' | 'outreach';
type IntelTab = 'pain-points' | 'product-fit' | 'insights' | 'call-prep' | 'notes';
type ContentTab = 'email' | 'call' | 'linkedin';

export default function ContactDetailModal({ 
  contact, 
  onClose, 
  onEnrichmentComplete 
}: ContactDetailModalProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('intelligence');
  const [activeIntelTab, setActiveIntelTab] = useState<IntelTab>('pain-points');
  const [activeContentTab, setActiveContentTab] = useState<ContentTab>('email');
  const [enriching, setEnriching] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [localContact, setLocalContact] = useState<Contact>(contact);
  const [notes, setNotes] = useState(contact.notes || '');
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [showEnrichSuccess, setShowEnrichSuccess] = useState(false);

  const isEnriched = localContact.enrichment_status === 'completed' || 
                     localContact.profile_content?.length > 0;

  const hasContent = localContact.email_1_subject || localContact.email_1_body;

  // Parse enrichment data with fallbacks
  let parsedData: any = {};
  try {
    if (localContact.enrichment_data) {
      parsedData = JSON.parse(localContact.enrichment_data);
    }
  } catch (e) {
    console.error('Failed to parse enrichment data:', e);
  }

  // Enhanced data extraction from structured enrichment profile
  const extractStructuredData = () => {
    const profile = localContact.profile_content || '';
    const data: any = {};

    const extractSection = (sectionNumber: string, sectionName: string) => {
      const regex = new RegExp(`## ${sectionNumber}\\. ${sectionName}[\\s\\S]*?(?=##|===|$)`, 'i');
      const match = profile.match(regex);
      return match ? match[0].replace(`## ${sectionNumber}. ${sectionName}`, '').trim() : null;
    };

    data.overview = extractSection('1', 'Overview');
    data.background = extractSection('2', 'Background');
    data.education = extractSection('3', 'Education');
    data.painPoints = extractSection('9', 'Pain Points');
    data.productFit = extractSection('10', 'Product Fit');
    data.keyInsights = extractSection('11', 'Key Insights');
    data.strategicSummary = extractSection('12', 'Final Note');

    return data;
  };

  const structuredData = extractStructuredData();

  const handleEnrich = async () => {
    setEnriching(true);
    setShowEnrichSuccess(false);
    try {
      const res = await fetch(
        `http://localhost:8000/api/contacts/${contact.id}/enrich`,
        { method: 'POST' }
      );
      const data = await res.json();
      
      if (data.success) {
        const updatedRes = await fetch(
          `http://localhost:8000/api/contacts/${contact.id}`
        );
        const updatedContact = await updatedRes.json();
        setLocalContact(updatedContact);
        onEnrichmentComplete?.(updatedContact);
        setShowEnrichSuccess(true);
        setTimeout(() => setShowEnrichSuccess(false), 3000);
      }
    } catch (err) {
      console.error('Enrichment failed:', err);
    } finally {
      setEnriching(false);
    }
  };

  const handleGenerateContent = async () => {
    setGenerating(true);
    try {
      const res = await fetch(
        `http://localhost:8000/api/contacts/${contact.id}/generate-content`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content_type: 'all' })
        }
      );
      const data = await res.json();
      
      if (data.success) {
        const updatedRes = await fetch(
          `http://localhost:8000/api/contacts/${contact.id}`
        );
        const updatedContact = await updatedRes.json();
        setLocalContact(updatedContact);
      }
    } catch (err) {
      console.error('Content generation failed:', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveNotes = async () => {
    try {
      await fetch(`http://localhost:8000/api/contacts/${contact.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes })
      });
    } catch (err) {
      console.error('Failed to save notes:', err);
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

  const extractPainPoints = () => {
    if (structuredData.painPoints) return structuredData.painPoints;
    if (localContact.pain_points) return localContact.pain_points;
    if (parsedData.pain_points) return parsedData.pain_points;
    return null;
  };

  const extractProductFit = () => {
    if (structuredData.productFit) return structuredData.productFit;
    if (localContact.product_match) return localContact.product_match;
    if (parsedData.product_fit) return parsedData.product_fit;
    return null;
  };

  const extractCallPrep = () => {
    if (structuredData.strategicSummary) return structuredData.strategicSummary;
    if (localContact.recommended_action) return localContact.recommended_action;
    return null;
  };

  const extractInsights = () => {
    const insights: any = {};
    
    if (structuredData.overview || structuredData.background) {
      insights.professional = [
        structuredData.overview,
        structuredData.background
      ].filter(Boolean).join('\n\n');
    }
    
    if (structuredData.education) {
      insights.education = structuredData.education;
    }
    
    if (structuredData.keyInsights) {
      insights.strategicInsights = structuredData.keyInsights;
    }
    
    return insights;
  };

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.75)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        padding: 20,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
          borderRadius: 20,
          width: '95%',
          maxWidth: 1400,
          height: '90vh',
          overflow: 'hidden',
          boxShadow: '0 25px 50px -12px rgba(0,0,0,0.95)',
          border: '1px solid rgba(99,102,241,0.3)',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* HEADER */}
        <div
          style={{
            padding: '20px 32px',
            borderBottom: '1px solid rgba(148,163,184,0.25)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexShrink: 0,
          }}
        >
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 24, fontWeight: 700, color: '#e5e7eb' }}>
              {localContact.name}
            </div>
            <div style={{ fontSize: 14, color: '#9ca3af', marginTop: 4 }}>
              {localContact.title} at {localContact.company}
            </div>
            <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
              {localContact.email && (
                <div style={{ fontSize: 13, color: '#64748b' }}>
                  📧 {localContact.email}
                </div>
              )}
              {localContact.phone && (
                <div style={{ fontSize: 13, color: '#64748b' }}>
                  📞 {localContact.phone}
                </div>
              )}
            </div>
          </div>

          {/* Right Side Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {/* Enrich Button */}
            <button
              onClick={handleEnrich}
              disabled={enriching}
              style={{
                padding: '12px 20px',
                borderRadius: 10,
                border: enriching 
                  ? '2px solid rgba(168,85,247,0.4)'
                  : '2px solid rgba(168,85,247,0.6)',
                background: enriching
                  ? 'linear-gradient(135deg, rgba(168,85,247,0.3), rgba(147,51,234,0.3))'
                  : 'linear-gradient(135deg, rgba(168,85,247,0.25), rgba(147,51,234,0.25))',
                color: '#e5e7eb',
                fontSize: 13,
                fontWeight: 700,
                cursor: enriching ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                transition: 'all 0.2s',
                boxShadow: enriching 
                  ? '0 0 20px rgba(168,85,247,0.4)'
                  : '0 4px 12px rgba(168,85,247,0.2)',
                transform: enriching ? 'scale(0.98)' : 'scale(1)',
              }}
            >
              {enriching ? (
                <>
                  <Loader size={16} style={{ animation: 'spin 1s linear infinite' }} />
                  AI Enriching...
                </>
              ) : showEnrichSuccess ? (
                <>
                  <Check size={16} />
                  Enriched!
                </>
              ) : (
                <>
                  <Zap size={16} />
                  {isEnriched ? 'Re-Enrich' : 'Enrich'}
                </>
              )}
            </button>

            {/* ADD TO CADENCE BUTTON - NEW */}
            <button
              onClick={async () => {
                const cadenceType = window.prompt(
                  'Select cadence type:\n\naggressive - 7 days, 5 touches (hot leads)\nstandard - 14 days, 5 touches (balanced)\nnurture - 30 days, 5 touches (long-term)\n\nEnter type:',
                  'standard'
                );
                
                if (!cadenceType) return;
                
                if (!['aggressive', 'standard', 'nurture'].includes(cadenceType)) {
                  alert('❌ Invalid cadence type');
                  return;
                }
                
                try {
                  const res = await fetch('http://localhost:8000/api/cadences/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      contact_id: contact.id,
                      type: cadenceType
                    })
                  });
                  
                  const data = await res.json();
                  if (data.success) {
                    alert(`✅ Added to ${cadenceType} cadence!\n${data.touches_scheduled} touches scheduled`);
                  } else {
                    alert(`❌ ${data.error}`);
                  }
                } catch (err) {
                  console.error(err);
                  alert('❌ Failed to add to cadence');
                }
              }}
              style={{
                padding: '12px 20px',
                borderRadius: 10,
                border: '2px solid rgba(34,197,94,0.6)',
                background: 'linear-gradient(135deg, rgba(34,197,94,0.25), rgba(16,185,129,0.25))',
                color: '#e5e7eb',
                fontSize: 13,
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                transition: 'all 0.2s',
                boxShadow: '0 4px 12px rgba(34,197,94,0.2)',
              }}
            >
              <Calendar size={16} />
              Add to Cadence
            </button>

            {/* Close Button */}
            <button
              onClick={onClose}
              style={{
                padding: 10,
                borderRadius: 8,
                border: '1px solid rgba(148,163,184,0.3)',
                background: 'transparent',
                color: '#9ca3af',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                transition: 'all 0.2s',
              }}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* MODE TOGGLE */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 0,
            borderBottom: '1px solid rgba(148,163,184,0.25)',
            background: 'rgba(15,23,42,0.5)',
            flexShrink: 0,
          }}
        >
          <button
            onClick={() => setViewMode('intelligence')}
            style={{
              padding: '16px',
              border: 'none',
              borderRight: '1px solid rgba(148,163,184,0.25)',
              borderBottom: viewMode === 'intelligence' 
                ? '3px solid rgba(99,102,241,0.8)'
                : '3px solid transparent',
              background: viewMode === 'intelligence'
                ? 'linear-gradient(135deg, rgba(79,70,229,0.15), rgba(99,102,241,0.15))'
                : 'transparent',
              color: viewMode === 'intelligence' ? '#e5e7eb' : '#9ca3af',
              fontSize: 15,
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 10,
              letterSpacing: 0.3,
            }}
          >
            <Lightbulb size={18} />
            Intelligence
          </button>
          <button
            onClick={() => setViewMode('outreach')}
            style={{
              padding: '16px',
              border: 'none',
              borderBottom: viewMode === 'outreach' 
                ? '3px solid rgba(99,102,241,0.8)'
                : '3px solid transparent',
              background: viewMode === 'outreach'
                ? 'linear-gradient(135deg, rgba(79,70,229,0.15), rgba(99,102,241,0.15))'
                : 'transparent',
              color: viewMode === 'outreach' ? '#e5e7eb' : '#9ca3af',
              fontSize: 15,
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.2s',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 10,
              letterSpacing: 0.3,
            }}
          >
            <Mail size={18} />
            Outreach
          </button>
        </div>

        {/* INTELLIGENCE MODE */}
        {viewMode === 'intelligence' && (
          <>
            <div
              style={{
                display: 'flex',
                gap: 4,
                padding: '12px 32px',
                borderBottom: '1px solid rgba(148,163,184,0.25)',
                background: 'rgba(15,23,42,0.3)',
                flexShrink: 0,
              }}
            >
              {[
                { id: 'pain-points', label: 'Pain Points', icon: Target },
                { id: 'product-fit', label: 'Product Fit', icon: Sparkles },
                { id: 'insights', label: 'Key Insights', icon: Lightbulb },
                { id: 'call-prep', label: 'Call Prep', icon: PhoneCall },
                { id: 'notes', label: 'Notes', icon: StickyNote },
              ].map((tab) => {
                const Icon = tab.icon;
                const active = activeIntelTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveIntelTab(tab.id as IntelTab)}
                    style={{
                      padding: '8px 16px',
                      borderRadius: 6,
                      border: 'none',
                      background: active
                        ? 'rgba(99,102,241,0.15)'
                        : 'transparent',
                      color: active ? '#e5e7eb' : '#9ca3af',
                      fontSize: 13,
                      fontWeight: 600,
                      cursor: 'pointer',
                      transition: 'all 0.15s',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                    }}
                  >
                    <Icon size={14} />
                    {tab.label}
                  </button>
                );
              })}
            </div>

            <div style={{ flex: 1, overflow: 'auto', padding: 32 }}>
              {!isEnriched ? (
                <div style={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#9ca3af',
                }}>
                  <Zap size={56} style={{ marginBottom: 20, color: '#a855f7' }} />
                  <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 12, color: '#e5e7eb' }}>
                    Ready to Unlock Intelligence
                  </div>
                  <div style={{ fontSize: 14, textAlign: 'center', maxWidth: 450, lineHeight: 1.6 }}>
                    Click the <span style={{ color: '#a855f7', fontWeight: 600 }}>Enrich</span> button above.
                  </div>
                </div>
              ) : (
                <>
                  {activeIntelTab === 'pain-points' && (
                    <IntelligenceSection
                      title="Pain Points & Challenges"
                      content={extractPainPoints()}
                      fallback="No specific pain points identified yet."
                      icon={<Target size={20} style={{ color: '#f97316' }} />}
                    />
                  )}
                  {activeIntelTab === 'product-fit' && (
                    <IntelligenceSection
                      title="Product Match Analysis"
                      content={extractProductFit()}
                      fallback="Product fit analysis not available yet."
                      icon={<Sparkles size={20} style={{ color: '#22c55e' }} />}
                    />
                  )}
                  {activeIntelTab === 'insights' && (
                    <div>
                      {(() => {
                        const insights = extractInsights();
                        return Object.keys(insights).length === 0 ? (
                          <div style={{ textAlign: 'center', color: '#9ca3af', padding: 40 }}>
                            No detailed insights available yet.
                          </div>
                        ) : (
                          <>
                            {insights.professional && (
                              <div style={{ marginBottom: 24 }}>
                                <IntelligenceSection
                                  title="Professional Overview"
                                  content={insights.professional}
                                  icon={<Lightbulb size={20} style={{ color: '#6366f1' }} />}
                                />
                              </div>
                            )}
                            {insights.education && (
                              <div style={{ marginBottom: 24 }}>
                                <IntelligenceSection
                                  title="Education & Background"
                                  content={insights.education}
                                  icon={<Target size={20} style={{ color: '#22c55e' }} />}
                                />
                              </div>
                            )}
                            {insights.strategicInsights && (
                              <div style={{ marginBottom: 24 }}>
                                <IntelligenceSection
                                  title="Strategic Intelligence"
                                  content={insights.strategicInsights}
                                  icon={<Zap size={20} style={{ color: '#a855f7' }} />}
                                />
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </div>
                  )}
                  {activeIntelTab === 'call-prep' && (
                    <div>
                      <IntelligenceSection
                        title="Strategic Call Summary"
                        content={extractCallPrep()}
                        fallback="No specific call strategy identified yet."
                        icon={<PhoneCall size={20} style={{ color: '#22c55e' }} />}
                      />
                      <div style={{ marginTop: 32 }}>
                        <div style={{ fontSize: 15, fontWeight: 600, color: '#9ca3af', marginBottom: 16 }}>
                          Scoring Summary
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
                          <ScoreCard label="MDCP Score" value={localContact.mdcp_score} color="#22c55e" />
                          <ScoreCard label="RSS Score" value={localContact.rss_score} color="#f97316" />
                          <ScoreCard label="Priority" value={localContact.priority_score} color="#6366f1" />
                        </div>
                      </div>
                    </div>
                  )}
                  {activeIntelTab === 'notes' && (
                    <div>
                      <div style={{ fontSize: 17, fontWeight: 600, color: '#e5e7eb', marginBottom: 16 }}>
                        Internal Notes
                      </div>
                      <textarea
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        onBlur={handleSaveNotes}
                        placeholder="Add your notes about this contact..."
                        style={{
                          width: '100%',
                          minHeight: 250,
                          padding: 20,
                          borderRadius: 10,
                          border: '1px solid rgba(148,163,184,0.3)',
                          background: 'rgba(15,23,42,0.6)',
                          color: '#e5e7eb',
                          fontSize: 14,
                          lineHeight: 1.7,
                          resize: 'vertical',
                          fontFamily: 'inherit',
                        }}
                      />
                    </div>
                  )}
                </>
              )}
            </div>
          </>
        )}

        {/* OUTREACH MODE */}
        {viewMode === 'outreach' && (
          <>
            <div
              style={{
                display: 'flex',
                gap: 4,
                padding: '12px 32px',
                borderBottom: '1px solid rgba(148,163,184,0.25)',
                background: 'rgba(15,23,42,0.3)',
                flexShrink: 0,
              }}
            >
              {[
                { id: 'email', label: 'Email Sequence', icon: Mail },
                { id: 'call', label: 'Call Scripts', icon: Phone },
                { id: 'linkedin', label: 'LinkedIn Messages', icon: Linkedin },
              ].map((tab) => {
                const Icon = tab.icon;
                const active = activeContentTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveContentTab(tab.id as ContentTab)}
                    style={{
                      padding: '8px 16px',
                      borderRadius: 6,
                      border: 'none',
                      background: active ? 'rgba(99,102,241,0.15)' : 'transparent',
                      color: active ? '#e5e7eb' : '#9ca3af',
                      fontSize: 13,
                      fontWeight: 600,
                      cursor: 'pointer',
                      transition: 'all 0.15s',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                    }}
                  >
                    <Icon size={14} />
                    {tab.label}
                  </button>
                );
              })}
            </div>

            <div style={{ flex: 1, overflow: 'auto', padding: 32 }}>
              {!isEnriched ? (
                <div style={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#9ca3af',
                }}>
                  <AlertCircle size={48} style={{ marginBottom: 16, color: '#64748b' }} />
                  <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
                    Enrich Contact First
                  </div>
                </div>
              ) : !hasContent ? (
                <div style={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#9ca3af',
                }}>
                  <Sparkles size={56} style={{ marginBottom: 20, color: '#6366f1' }} />
                  <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 12, color: '#e5e7eb' }}>
                    Generate AI-Powered Outreach
                  </div>
                  <button
                    onClick={handleGenerateContent}
                    disabled={generating}
                    style={{
                      padding: '14px 28px',
                      borderRadius: 10,
                      border: '2px solid rgba(99,102,241,0.6)',
                      background: generating
                        ? 'rgba(71,85,105,0.5)'
                        : 'linear-gradient(135deg, rgba(79,70,229,0.4), rgba(99,102,241,0.4))',
                      color: '#e5e7eb',
                      fontSize: 15,
                      fontWeight: 700,
                      cursor: generating ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 10,
                    }}
                  >
                    {generating ? (
                      <>
                        <Loader size={18} style={{ animation: 'spin 1s linear infinite' }} />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles size={18} />
                        Generate All Content
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <>
                  <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between' }}>
                    <div style={{ fontSize: 13, color: '#9ca3af' }}>
                      AI-generated outreach content
                    </div>
                    <button onClick={handleGenerateContent} disabled={generating} style={{
                      padding: '8px 16px',
                      borderRadius: 6,
                      border: '1px solid rgba(99,102,241,0.5)',
                      background: 'rgba(79,70,229,0.2)',
                      color: '#e5e7eb',
                      fontSize: 13,
                      fontWeight: 600,
                      cursor: generating ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                    }}>
                      <RefreshCw size={14} />
                      Regenerate
                    </button>
                  </div>

                  {activeContentTab === 'email' && (
                    <EmailContent 
                      contact={localContact} 
                      copyToClipboard={copyToClipboard}
                      copiedField={copiedField}
                    />
                  )}
                  {activeContentTab === 'call' && (
                    <CallScriptContent 
                      contact={localContact}
                      copyToClipboard={copyToClipboard}
                      copiedField={copiedField}
                    />
                  )}
                  {activeContentTab === 'linkedin' && (
                    <LinkedInContent 
                      contact={localContact}
                      copyToClipboard={copyToClipboard}
                      copiedField={copiedField}
                    />
                  )}
                </>
              )}
            </div>
          </>
        )}
      </div>

      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
}

// Helper Components
function IntelligenceSection({ 
  title, 
  content, 
  fallback,
  icon
}: { 
  title: string; 
  content?: string; 
  fallback?: string;
  icon?: React.ReactNode;
}) {
  return (
    <div>
      <div style={{ 
        fontSize: 17, 
        fontWeight: 600, 
        color: '#e5e7eb',
        marginBottom: 16,
        display: 'flex',
        alignItems: 'center',
        gap: 10,
      }}>
        {icon}
        {title}
      </div>
      <div style={{ 
        padding: 20, 
        background: 'rgba(15,23,42,0.6)',
        borderRadius: 10,
        border: '1px solid rgba(148,163,184,0.2)',
        color: content ? '#d1d5db' : '#64748b',
        fontSize: 14,
        lineHeight: 1.7,
        whiteSpace: 'pre-wrap',
      }}>
        {content || fallback || 'No data available'}
      </div>
    </div>
  );
}

function ScoreCard({ label, value, color }: { label: string; value?: number; color: string }) {
  return (
    <div style={{ 
      padding: 20, 
      background: 'rgba(15,23,42,0.6)',
      borderRadius: 10,
      border: '1px solid rgba(148,163,184,0.2)',
      textAlign: 'center',
    }}>
      <div style={{ fontSize: 12, color: '#9ca3af', marginBottom: 8 }}>
        {label}
      </div>
      <div style={{ fontSize: 32, fontWeight: 800, color }}>
        {value != null ? Math.round(value) : '—'}
      </div>
    </div>
  );
}

function EmailContent({ 
  contact, 
  copyToClipboard, 
  copiedField 
}: { 
  contact: Contact;
  copyToClipboard: (text: string, field: string) => void;
  copiedField: string | null;
}) {
  const cleanContent = (text: string | undefined, type: 'subject' | 'body'): string => {
    if (!text) return '';
    let cleaned = text.trim();
    if (type === 'subject') {
      cleaned = cleaned.replace(/^Subject:\s*/i, '');
    } else {
      cleaned = cleaned.replace(/^Subject:.*?\n\n/i, '');
      cleaned = cleaned.replace(/^Body:\s*/i, '');
    }
    return cleaned;
  };

  const emails = [
    { 
      subject: cleanContent(contact.email_1_subject, 'subject'), 
      body: cleanContent(contact.email_1_body, 'body'), 
      label: 'Email 1 - Introduction',
      description: 'Initial outreach',
      color: '#6366f1'
    },
    { 
      subject: cleanContent(contact.email_2_subject, 'subject'), 
      body: cleanContent(contact.email_2_body, 'body'), 
      label: 'Email 2 - Value Add',
      description: 'Follow-up',
      color: '#22c55e'
    },
    { 
      subject: cleanContent(contact.email_3_subject, 'subject'), 
      body: cleanContent(contact.email_3_body, 'body'), 
      label: 'Email 3 - Action',
      description: 'Call-to-action',
      color: '#f97316'
    },
  ].filter(e => e.subject && e.body);

  if (emails.length === 0) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: '#9ca3af' }}>
        <Mail size={48} style={{ marginBottom: 16, color: '#64748b' }} />
        <div>No Email Content Generated Yet</div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
      {emails.map((email, idx) => (
        <div key={idx} style={{
          padding: 0,
          background: 'rgba(15,23,42,0.6)',
          borderRadius: 16,
          border: `1px solid ${email.color}40`,
          overflow: 'hidden',
        }}>
          <div style={{ 
            padding: '20px 28px',
            background: `linear-gradient(135deg, ${email.color}15, ${email.color}08)`,
            borderBottom: `1px solid ${email.color}30`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}>
            <div style={{ fontSize: 16, fontWeight: 700, color: '#e5e7eb' }}>
              {email.label}
            </div>
            <button
              onClick={() => copyToClipboard(`Subject: ${email.subject}\n\n${email.body}`, `email-${idx}`)}
              style={{
                padding: '10px 20px',
                borderRadius: 8,
                border: `1px solid ${email.color}60`,
                background: copiedField === `email-${idx}` ? 'rgba(34,197,94,0.25)' : `${email.color}20`,
                color: '#e5e7eb',
                fontSize: 13,
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              {copiedField === `email-${idx}` ? <><Check size={16} />Copied!</> : <><Copy size={16} />Copy All</>}
            </button>
          </div>
          
          <div style={{ padding: 28 }}>
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontSize: 11, color: '#9ca3af', marginBottom: 10, textTransform: 'uppercase' }}>
                Subject Line
              </div>
              <div style={{ 
                padding: 18,
                background: 'rgba(30,41,59,0.8)',
                borderRadius: 10,
                color: '#f3f4f6',
                fontSize: 15,
                lineHeight: 1.5,
              }}>
                {email.subject}
              </div>
            </div>

            <div>
              <div style={{ fontSize: 11, color: '#9ca3af', marginBottom: 10, textTransform: 'uppercase' }}>
                Email Body
              </div>
              <div style={{ 
                padding: 20,
                background: 'rgba(30,41,59,0.5)',
                borderRadius: 10,
                color: '#e5e7eb',
                fontSize: 14,
                lineHeight: 1.8,
                whiteSpace: 'pre-wrap',
              }}>
                {email.body}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function CallScriptContent({ contact, copyToClipboard, copiedField }: any) {
  return <div style={{ color: '#9ca3af' }}>Call scripts coming soon...</div>;
}

function LinkedInContent({ contact, copyToClipboard, copiedField }: any) {
  return <div style={{ color: '#9ca3af' }}>LinkedIn messages coming soon...</div>;
}
