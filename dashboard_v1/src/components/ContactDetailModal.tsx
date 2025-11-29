import React, { useState, useEffect } from 'react';
import {
  X, Sparkles, Loader, Mail, Phone, Linkedin, Target, Lightbulb,
  PhoneCall, StickyNote, Copy, Check, Zap, FileText, User, Building2,
  Award, TrendingUp, ChevronRight, Rocket
} from 'lucide-react';
import ActivityLogger from './ActivityLogger';
import ActivityTimeline from './ActivityTimeline';

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
  call_script_1?: string;
  call_script_2?: string;
  call_script_3?: string;
  linkedin_connect?: string;
  linkedin_followup?: string;
  linkedin_inmail?: string;
  linkedin_warmup?: string;
  linkedin_url?: string;
}

interface ContactDetailModalProps {
  contact: Contact;
  onClose: () => void;
  onEnrichmentComplete?: (contact: Contact) => void;
}

type ViewMode = 'intelligence' | 'outreach' | 'dossier';
type IntelTab = 'pain-points' | 'product-fit' | 'insights' | 'call-prep' | 'notes';
type DossierTab = 'professional' | 'company' | 'personality';
type ContentTab = 'email' | 'call' | 'linkedin';

export default function ContactDetailModal({ contact, onClose, onEnrichmentComplete }: ContactDetailModalProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('intelligence');
  const [activeIntelTab, setActiveIntelTab] = useState<IntelTab>('pain-points');
  const [activeDossierTab, setActiveDossierTab] = useState<DossierTab>('professional');
  const [activeContentTab, setActiveContentTab] = useState<ContentTab>('email');
  const [enriching, setEnriching] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [localContact, setLocalContact] = useState(contact);
  const [notes, setNotes] = useState(contact.notes || '');
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [showEnrichSuccess, setShowEnrichSuccess] = useState(false);
  const [showGenerateSuccess, setShowGenerateSuccess] = useState(false);
  const [justEnriched, setJustEnriched] = useState(false);

  useEffect(() => {
    fetch(`https://apex-intelligence-production.up.railway.app/api/contacts/${contact.id}`)
      .then(res => res.json())
      .then(data => {
        setLocalContact(data);
        setNotes(data.notes || '');
      })
      .catch(err => console.error('Fetch failed:', err));
  }, [contact.id]);

  const isEnriched = localContact.enrichment_status === 'completed' && localContact.profile_content && localContact.profile_content.length > 0;
  const hasContent = !!(localContact.email_1_subject || localContact.email_1_body || localContact.call_script_1 || localContact.linkedin_connect);

  const extractSection = (sectionNumber: string, sectionName: string): string | null => {
    const profile = localContact.profile_content || '';
    const regex = new RegExp(`${sectionNumber}\\.\\s*${sectionName}[:\\s]*`, 'i');
    const match = profile.match(regex);
    if (!match) return null;
    const startPos = match.index! + match[0].length;
    let endPos = profile.length;
    for (let i = startPos; i < profile.length - 3; i++) {
      if (profile[i].match(/\d/) && profile[i + 1] === '.' && profile[i + 2] === ' ') {
        endPos = i;
        break;
      }
    }
    return profile.substring(startPos, endPos).trim();
  };

  const dossierData = {
    overview: extractSection('1', 'Professional Background'),
    background: extractSection('2', 'Background'),
    education: extractSection('3', 'Education'),
    recentMentions: extractSection('4', 'Recent Activity'),
    socialProfiles: extractSection('5', 'Social Profiles'),
    personality: extractSection('6', 'Communication Style'),
    myersBriggs: extractSection('7', 'Myers-Briggs'),
    companyOverview: extractSection('8', 'Company Overview'),
    painPoints: extractSection('9', 'Potential Pain Points'),
    productFit: extractSection('10', 'Product Fit'),
    keyInsights: extractSection('11', 'Talking Points'),
    finalNote: extractSection('12', 'Industry Context'),
  };

  const handleEnrich = async () => {
    setEnriching(true);
    setShowEnrichSuccess(false);
    setJustEnriched(false);
    try {
      const res = await fetch(`https://apex-intelligence-production.up.railway.app/api/contacts/${contact.id}/enrich`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        const updatedRes = await fetch(`https://apex-intelligence-production.up.railway.app/api/contacts/${contact.id}`);
        const updatedContact = await updatedRes.json();
        setLocalContact(updatedContact);
        onEnrichmentComplete?.(updatedContact);
        setShowEnrichSuccess(true);
        setJustEnriched(true);
        setViewMode('intelligence');
        setActiveIntelTab('pain-points');
        setTimeout(() => setShowEnrichSuccess(false), 5000);
      }
    } catch (err) {
      console.error('Enrichment failed:', err);
    } finally {
      setEnriching(false);
    }
  };

  const handleGenerateContent = async () => {
    setGenerating(true);
    setShowGenerateSuccess(false);
    try {
      const res = await fetch(`https://apex-intelligence-production.up.railway.app/api/contacts/${contact.id}/generate-content`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content_type: 'all' }),
      });
      const data = await res.json();
      const updatedRes = await fetch(`https://apex-intelligence-production.up.railway.app/api/contacts/${contact.id}`);
      const updatedContact = await updatedRes.json();
      setLocalContact(updatedContact);
      onEnrichmentComplete?.(updatedContact);
      if (data.success || data.results) {
        setShowGenerateSuccess(true);
        setJustEnriched(false);
        setViewMode('outreach');
        setActiveContentTab('email');
        setTimeout(() => setShowGenerateSuccess(false), 3000);
      }
    } catch (err) {
      console.error('Content generation failed:', err);
      try {
        const updatedRes = await fetch(`https://apex-intelligence-production.up.railway.app/api/contacts/${contact.id}`);
        const updatedContact = await updatedRes.json();
        setLocalContact(updatedContact);
      } catch {}
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveNotes = async () => {
    try {
      await fetch(`https://apex-intelligence-production.up.railway.app/api/contacts/${contact.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes }),
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

  return (
    <>
      <div
        onClick={onClose}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.85)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: 20
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
          {/* SUCCESS BANNER */}
          {showEnrichSuccess && (
            <div style={{ background: 'linear-gradient(135deg, #10b981, #059669)', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: 16, fontWeight: 700, color: 'white', marginBottom: 4 }}>
                  <Sparkles size={18} style={{ display: 'inline', marginRight: 8 }} />
                  Intelligence Unlocked!
                </div>
                <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.9)' }}>
                  Explore insights, personality, and company intel
                </div>
              </div>
              <button
                onClick={() => { setViewMode('outreach'); setShowEnrichSuccess(false); }}
                style={{
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  border: 'none',
                  borderRadius: 8,
                  padding: '10px 20px',
                  color: 'white',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                <Rocket size={16} style={{ display: 'inline', marginRight: 6 }} />
                Generate Outreach →
              </button>
            </div>
          )}

          {/* HEADER */}
          <div style={{ padding: '20px 32px', borderBottom: '1px solid rgba(148,163,184,0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                <div style={{
                  width: 48,
                  height: 48,
                  borderRadius: 999,
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: 18,
                  fontWeight: 700
                }}>
                  {localContact.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()}
                </div>
                <div>
                  <h2 style={{ fontSize: 20, fontWeight: 700, color: '#e5e7eb', marginBottom: 4 }}>{localContact.name}</h2>
                  <div style={{ fontSize: 13, color: '#9ca3af' }}>{localContact.title} at {localContact.company}</div>
                </div>
                <StatusBadge contact={localContact} />
              </div>
              <div style={{ display: 'flex', gap: 12, fontSize: 12, color: '#9ca3af' }}>
                {localContact.email && <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Mail size={14} />{localContact.email}</div>}
                {localContact.phone && <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Phone size={14} />{localContact.phone}</div>}
              </div>
            </div>

            <div style={{ display: 'flex', gap: 8 }}>
              <button
                onClick={handleEnrich}
                disabled={enriching}
                style={{
                  padding: '10px 20px',
                  borderRadius: 8,
                  border: '1px solid rgba(99,102,241,0.5)',
                  background: enriching ? 'rgba(30,41,59,0.5)' : 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2))',
                  color: enriching ? '#64748b' : '#a5b4fc',
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: enriching ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8
                }}
              >
                {enriching ? (
                  <>
                    <Loader size={16} style={{ animation: 'spin 1s linear infinite' }} />
                    Enriching...
                  </>
                ) : showEnrichSuccess ? (
                  <>
                    <Check size={16} />
                    Enriched!
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    {isEnriched ? 'Re-Enrich' : 'Enrich'}
                  </>
                )}
              </button>
              <button onClick={onClose} style={{ width: 40, height: 40, borderRadius: 8, border: '1px solid rgba(148,163,184,0.3)', background: 'rgba(30,41,59,0.6)', color: '#9ca3af', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <X size={20} />
              </button>
            </div>
          </div>

          {/* GENERATE CONTENT CTA */}
          {justEnriched && !hasContent && !showEnrichSuccess && (
            <div style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.15))', padding: '16px 32px', borderBottom: '1px solid rgba(99,102,241,0.3)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, color: '#e5e7eb', marginBottom: 4 }}>
                  <Zap size={16} style={{ display: 'inline', marginRight: 6, color: '#fbbf24' }} />
                  Ready for Next Step
                </div>
                <div style={{ fontSize: 12, color: '#9ca3af' }}>Generate personalized emails, call scripts, and LinkedIn messages</div>
              </div>
              <button
                onClick={handleGenerateContent}
                disabled={generating}
                style={{
                  padding: '10px 20px',
                  borderRadius: 8,
                  border: 'none',
                  background: generating ? 'rgba(71,85,105,0.5)' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  color: 'white',
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: generating ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8
                }}
              >
                {generating ? (
                  <>
                    <Loader size={16} style={{ animation: 'spin 1s linear infinite' }} />
                    Generating...
                  </>
                ) : (
                  <>
                    <Rocket size={16} />
                    Generate All Content
                  </>
                )}
              </button>
            </div>
          )}

          {/* MODE TABS */}
          <div style={{ display: 'flex', borderBottom: '1px solid rgba(148,163,184,0.2)' }}>
            {[
              { id: 'intelligence', label: 'Intelligence', icon: Target, badge: isEnriched ? '✓' : null },
              { id: 'dossier', label: 'Dossier', icon: FileText },
              { id: 'outreach', label: 'Outreach', icon: Mail, badge: hasContent ? '✓' : null }
            ].map((mode) => {
              const Icon = mode.icon;
              return (
                <button
                  key={mode.id}
                  onClick={() => setViewMode(mode.id as ViewMode)}
                  style={{
                    flex: 1,
                    padding: 16,
                    border: 'none',
                    borderBottom: viewMode === mode.id ? '3px solid #6366f1' : '3px solid transparent',
                    background: viewMode === mode.id ? 'rgba(99,102,241,0.1)' : 'transparent',
                    color: viewMode === mode.id ? '#e5e7eb' : '#9ca3af',
                    fontSize: 15,
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 10,
                    position: 'relative'
                  }}
                >
                  <Icon size={18} />
                  {mode.label}
                  {mode.badge && (
                    <span style={{ position: 'absolute', top: 8, right: 8, background: '#10b981', color: 'white', fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 999 }}>
                      {mode.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* CONTENT AREA */}
          <div style={{ flex: 1, overflow: 'auto', padding: '24px 32px' }}>
            {viewMode === 'intelligence' && (
              <>
                <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
                  {[
                    { id: 'pain-points', label: 'Pain Points', icon: Target },
                    { id: 'product-fit', label: 'Product Fit', icon: Sparkles },
                    { id: 'insights', label: 'Insights', icon: Lightbulb },
                    { id: 'call-prep', label: 'Call Prep', icon: PhoneCall },
                    { id: 'notes', label: 'Notes', icon: StickyNote }
                  ].map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveIntelTab(tab.id as IntelTab)}
                        style={{
                          padding: '8px 16px',
                          borderRadius: 6,
                          border: 'none',
                          background: activeIntelTab === tab.id ? 'rgba(99,102,241,0.15)' : 'transparent',
                          color: activeIntelTab === tab.id ? '#e5e7eb' : '#9ca3af',
                          fontSize: 13,
                          fontWeight: 600,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 6
                        }}
                      >
                        <Icon size={16} />
                        {tab.label}
                      </button>
                    );
                  })}
                </div>

                {!isEnriched ? (
                  <EmptyState
                    icon={<Sparkles size={48} color="#6366f1" />}
                    title="Ready to Unlock Intelligence"
                    subtitle="Click the Enrich button above to discover pain points, personality insights, and more."
                  />
                ) : (
                  <>
                    {activeIntelTab === 'pain-points' && (
                      <ContentSection
                        title="Pain Points"
                        content={dossierData.painPoints}
                        icon={<Target size={20} color="#ef4444" />}
                      />
                    )}
                    {activeIntelTab === 'product-fit' && (
                      <ContentSection
                        title="Product Fit Analysis"
                        content={dossierData.productFit}
                        icon={<Sparkles size={20} color="#8b5cf6" />}
                      />
                    )}
                    {activeIntelTab === 'insights' && (
                      <ContentSection
                        title="Key Insights"
                        content={dossierData.keyInsights}
                        icon={<Lightbulb size={20} color="#fbbf24" />}
                      />
                    )}
                    {activeIntelTab === 'call-prep' && (
                      <>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 20 }}>
                          <ScoreCard label="Priority" value={localContact.priority_score} color="#22c55e" />
                          <ScoreCard label="MDCP" value={localContact.mdcp_score} color="#eab308" />
                          <ScoreCard label="RSS" value={localContact.rss_score} color="#06b6d4" />
                        </div>
                        <ContentSection
                          title="Call Preparation"
                          content={dossierData.finalNote}
                          icon={<PhoneCall size={20} color="#10b981" />}
                        />
                      </>
                    )}
                    {activeIntelTab === 'notes' && (
                      <div>
                        <h3 style={{ fontSize: 16, fontWeight: 600, color: '#e5e7eb', marginBottom: 12 }}>Internal Notes</h3>
                        <textarea
                          value={notes}
                          onChange={(e) => setNotes(e.target.value)}
                          onBlur={handleSaveNotes}
                          placeholder="Add notes about this contact..."
                          style={{
                            width: '100%',
                            minHeight: 250,
                            padding: 16,
                            borderRadius: 10,
                            border: '1px solid rgba(148,163,184,0.3)',
                            background: 'rgba(15,23,42,0.6)',
                            color: '#e5e7eb',
                            fontSize: 14,
                            lineHeight: 1.6,
                            resize: 'vertical'
                          }}
                        />
                      </div>
                    )}
                  </>
                )}
              </>
            )}

            {viewMode === 'dossier' && (
              <>
                <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
                  {[
                    { id: 'professional', label: 'Professional', icon: User },
                    { id: 'company', label: 'Company', icon: Building2 },
                    { id: 'personality', label: 'Personality', icon: Award }
                  ].map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveDossierTab(tab.id as DossierTab)}
                        style={{
                          padding: '8px 16px',
                          borderRadius: 6,
                          border: 'none',
                          background: activeDossierTab === tab.id ? 'rgba(99,102,241,0.15)' : 'transparent',
                          color: activeDossierTab === tab.id ? '#e5e7eb' : '#9ca3af',
                          fontSize: 13,
                          fontWeight: 600,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 6
                        }}
                      >
                        <Icon size={16} />
                        {tab.label}
                      </button>
                    );
                  })}
                </div>

                {!isEnriched ? (
                  <EmptyState
                    icon={<FileText size={48} color="#6366f1" />}
                    title="No Dossier Available"
                    subtitle="Enrich this contact first to view their full profile."
                  />
                ) : (
                  <>
                    {activeDossierTab === 'professional' && (
                      <>
                        <DossierCard title="Overview" content={dossierData.overview} icon={<User size={18} color="#6366f1" />} />
                        <DossierCard title="Background" content={dossierData.background} icon={<TrendingUp size={18} color="#8b5cf6" />} />
                        <DossierCard title="Education" content={dossierData.education} icon={<Award size={18} color="#10b981" />} />
                        <DossierCard title="Recent Mentions" content={dossierData.recentMentions} icon={<Sparkles size={18} color="#fbbf24" />} />
                      </>
                    )}
                    {activeDossierTab === 'company' && (
                      <DossierCard title="Company Overview" content={dossierData.companyOverview} icon={<Building2 size={18} color="#0ea5e9" />} />
                    )}
                    {activeDossierTab === 'personality' && (
                      <>
                        <DossierCard title="Personality Traits" content={dossierData.personality} icon={<Award size={18} color="#f59e0b" />} />
                        <DossierCard title="Myers-Briggs Type" content={dossierData.myersBriggs} icon={<Lightbulb size={18} color="#8b5cf6" />} />
                        <DossierCard title="Social Profiles" content={dossierData.socialProfiles} icon={<Linkedin size={18} color="#0ea5e9" />} />
                      </>
                    )}
                  </>
                )}
              </>
            )}

            {viewMode === 'outreach' && (
              <>
                <div style={{ display: 'flex', gap: 12, marginBottom: 20, alignItems: 'center' }}>
                  {[
                    { id: 'email', label: 'Email', icon: Mail, color: '#6366f1' },
                    { id: 'call', label: 'Call Scripts', icon: PhoneCall, color: '#10b981' },
                    { id: 'linkedin', label: 'LinkedIn', icon: Linkedin, color: '#0ea5e9' }
                  ].map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveContentTab(tab.id as ContentTab)}
                        style={{
                          padding: '10px 20px',
                          borderRadius: 8,
                          border: activeContentTab === tab.id ? `1px solid ${tab.color}` : '1px solid transparent',
                          background: activeContentTab === tab.id ? `${tab.color}15` : 'transparent',
                          color: activeContentTab === tab.id ? tab.color : '#9ca3af',
                          fontSize: 13,
                          fontWeight: 600,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 8
                        }}
                      >
                        <Icon size={16} />
                        {tab.label}
                      </button>
                    );
                  })}
                  <button
                    onClick={handleGenerateContent}
                    disabled={generating}
                    style={{
                      marginLeft: 'auto',
                      padding: '10px 16px',
                      borderRadius: 8,
                      border: 'none',
                      background: generating ? 'rgba(71,85,105,0.5)' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                      color: 'white',
                      fontSize: 12,
                      fontWeight: 600,
                      cursor: generating ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6
                    }}
                  >
                    {generating ? (
                      <>
                        <Loader size={14} style={{ animation: 'spin 1s linear infinite' }} />
                        Generating...
                      </>
                    ) : showGenerateSuccess ? (
                      <>
                        <Check size={14} />
                        Generated!
                      </>
                    ) : (
                      <>
                        <Zap size={14} />
                        Generate All Content
                      </>
                    )}
                  </button>
                </div>

                {!isEnriched ? (
                  <EmptyState
                    icon={<Sparkles size={48} color="#6366f1" />}
                    title="Enrich First"
                    subtitle="Generate intelligence before creating outreach content."
                  />
                ) : !hasContent ? (
                  <EmptyState
                    icon={<Rocket size={48} color="#8b5cf6" />}
                    title="Ready to Generate"
                    subtitle='Click "Generate All Content" to create personalized emails, call scripts, and LinkedIn messages.'
                  />
                ) : (
                  <>
                    {activeContentTab === 'email' && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                        {[1, 2, 3].map((num) => {
                          const subject = localContact[`email_${num}_subject` as keyof Contact] as string;
                          const body = localContact[`email_${num}_body` as keyof Contact] as string;
                          if (!subject && !body) return null;
                          return (
                            <EmailCard
                              key={num}
                              number={num}
                              subject={subject}
                              body={body}
                              onCopy={copyToClipboard}
                              copiedField={copiedField}
                            />
                          );
                        })}
                      </div>
                    )}

                    {activeContentTab === 'call' && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                        {[1, 2, 3].map((num) => {
                          const script = localContact[`call_script_${num}` as keyof Contact] as string;
                          if (!script) return null;
                          const labels = ['Direct & Value-Focused', 'Consultative & Rapport-Building', 'Executive / Insight-Led'];
                          return (
                            <CallScriptCard
                              key={num}
                              number={num}
                              label={labels[num - 1]}
                              content={script}
                              onCopy={copyToClipboard}
                              copiedField={copiedField}
                            />
                          );
                        })}
                      </div>
                    )}

                    {activeContentTab === 'linkedin' && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                        <LinkedInCard
                          title="Connection Request Message"
                          content={localContact.linkedin_connect}
                          onCopy={copyToClipboard}
                          copiedField={copiedField}
                          fieldKey="linkedin_connect"
                          maxChars={300}
                        />
                        <LinkedInCard
                          title="Follow-up Message"
                          content={localContact.linkedin_followup}
                          onCopy={copyToClipboard}
                          copiedField={copiedField}
                          fieldKey="linkedin_followup"
                        />
                        <LinkedInCard
                          title="InMail Template"
                          content={localContact.linkedin_inmail}
                          onCopy={copyToClipboard}
                          copiedField={copiedField}
                          fieldKey="linkedin_inmail"
                          maxChars={1900}
                        />
                        <LinkedInCard
                          title="Warm-up Sequence"
                          content={localContact.linkedin_warmup}
                          onCopy={copyToClipboard}
                          copiedField={copiedField}
                          fieldKey="linkedin_warmup"
                        />
                      </div>
                    )}
                  </>
                )}
              </>
            )}

            {/* ==================== ACTIVITY LOGGER & TIMELINE (PHASE 2) ==================== */}
            {isEnriched && (
              <>
                <div style={{ marginTop: 32, paddingTop: 24, borderTop: '1px solid rgba(148,163,184,0.2)' }}>
                  <ActivityLogger
                    contactId={localContact.id}
                    contactName={localContact.name}
                    onActivityLogged={() => {
                      fetch(`https://apex-intelligence-production.up.railway.app/api/contacts/${localContact.id}`)
                        .then(res => res.json())
                        .then(data => {
                          setLocalContact(data);
                          onEnrichmentComplete?.(data);
                        })
                        .catch(err => console.error('Refresh failed:', err));
                    }}
                  />
                </div>

                <div style={{ marginTop: 16 }}>
                  <ActivityTimeline contactId={localContact.id} />
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

// ==================== HELPER COMPONENTS ====================

function StatusBadge({ contact }: { contact: Contact }) {
  if (contact.call_script_1 || contact.email_1_body || contact.linkedin_connect) {
    return <span style={{ padding: '4px 10px', borderRadius: 999, background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.5)', color: '#10b981', fontSize: 11, fontWeight: 700 }}>✍️ Content Ready</span>;
  }
  if (contact.priority_score) {
    return <span style={{ padding: '4px 10px', borderRadius: 999, background: 'rgba(251,191,36,0.15)', border: '1px solid rgba(251,191,36,0.5)', color: '#fbbf24', fontSize: 11, fontWeight: 700 }}>🎯 Scored</span>;
  }
  if (contact.enrichment_status === 'completed') {
    return <span style={{ padding: '4px 10px', borderRadius: 999, background: 'rgba(139,92,246,0.15)', border: '1px solid rgba(139,92,246,0.5)', color: '#8b5cf6', fontSize: 11, fontWeight: 700 }}>✨ Enriched</span>;
  }
  return <span style={{ padding: '4px 10px', borderRadius: 999, background: 'rgba(71,85,105,0.15)', border: '1px solid rgba(71,85,105,0.5)', color: '#64748b', fontSize: 11, fontWeight: 700 }}>○ Pending</span>;
}

function EmptyState({ icon, title, subtitle }: { icon: React.ReactNode; title: string; subtitle: string }) {
  return (
    <div style={{ textAlign: 'center', padding: '60px 20px' }}>
      <div style={{ marginBottom: 16 }}>{icon}</div>
      <div style={{ fontSize: 18, fontWeight: 600, color: '#e5e7eb', marginBottom: 8 }}>{title}</div>
      <div style={{ fontSize: 14, color: '#9ca3af' }}>{subtitle}</div>
    </div>
  );
}

function ContentSection({ title, content, icon }: { title: string; content?: string | null; icon?: React.ReactNode }) {
  return (
    <div style={{ background: 'rgba(30,41,59,0.5)', borderRadius: 12, padding: 20, border: '1px solid rgba(148,163,184,0.2)', marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        {icon}
        <h3 style={{ fontSize: 16, fontWeight: 600, color: '#e5e7eb' }}>{title}</h3>
      </div>
      <div style={{ fontSize: 14, lineHeight: 1.7, color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>
        {content || 'No data available'}
      </div>
    </div>
  );
}

function DossierCard({ title, content, icon }: { title: string; content?: string | null; icon?: React.ReactNode }) {
  if (!content) return null;
  return (
    <div style={{ background: 'rgba(30,41,59,0.5)', borderRadius: 12, padding: 20, border: '1px solid rgba(148,163,184,0.2)', marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        {icon}
        <h3 style={{ fontSize: 16, fontWeight: 600, color: '#e5e7eb' }}>{title}</h3>
      </div>
      <div style={{ fontSize: 14, lineHeight: 1.7, color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>{content}</div>
    </div>
  );
}

function ScoreCard({ label, value, color }: { label: string; value?: number; color: string }) {
  return (
    <div style={{ background: 'rgba(30,41,59,0.5)', borderRadius: 12, padding: 20, border: '1px solid rgba(148,163,184,0.2)', textAlign: 'center' }}>
      <div style={{ fontSize: 12, color: '#9ca3af', marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: 32, fontWeight: 700, color }}>{value != null ? Math.round(value) : '—'}</div>
    </div>
  );
}

function EmailCard({ number, subject, body, onCopy, copiedField }: { number: number; subject: string; body: string; onCopy: (t: string, f: string) => void; copiedField: string | null }) {
  const labels = ['Initial Outreach', 'Follow-up', 'Break-up Email'];
  const colors = ['#6366f1', '#8b5cf6', '#a855f7'];
  const color = colors[number - 1];
  return (
    <div style={{ background: 'rgba(30,41,59,0.5)', borderRadius: 12, padding: 20, border: `1px solid ${color}30` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 600, color }}><Mail size={16} style={{ display: 'inline', marginRight: 6 }} />Email {number}</div>
          <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 4 }}>{labels[number - 1]}</div>
        </div>
        <button
          onClick={() => onCopy(`Subject: ${subject}\n\n${body}`, `email_${number}`)}
          style={{
            background: 'transparent',
            border: 'none',
            color: copiedField === `email_${number}` ? '#10b981' : '#64748b',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 12
          }}
        >
          {copiedField === `email_${number}` ? <Check size={16} /> : <Copy size={16} />}
          {copiedField === `email_${number}` ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: '#9ca3af', marginBottom: 4 }}>SUBJECT</div>
        <div style={{ fontSize: 13, color: '#e5e7eb', fontWeight: 500 }}>{subject}</div>
      </div>
      <div>
        <div style={{ fontSize: 11, fontWeight: 600, color: '#9ca3af', marginBottom: 4 }}>BODY</div>
        <div style={{ fontSize: 13, lineHeight: 1.7, color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>{body}</div>
      </div>
    </div>
  );
}

function CallScriptCard({ number, label, content, onCopy, copiedField }: { number: number; label: string; content: string; onCopy: (t: string, f: string) => void; copiedField: string | null }) {
  const colors = ['#10b981', '#22c55e', '#16a34a'];
  const color = colors[number - 1];
  return (
    <div style={{ background: 'rgba(30,41,59,0.5)', borderRadius: 12, padding: 20, border: `1px solid ${color}30` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 600, color }}><PhoneCall size={16} style={{ display: 'inline', marginRight: 6 }} />Script {number}</div>
          <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 4 }}>{label}</div>
        </div>
        <button
          onClick={() => onCopy(content, `call_script_${number}`)}
          style={{
            background: 'transparent',
            border: 'none',
            color: copiedField === `call_script_${number}` ? '#10b981' : '#64748b',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 12
          }}
        >
          {copiedField === `call_script_${number}` ? <Check size={16} /> : <Copy size={16} />}
          Copy
        </button>
      </div>
      <div style={{ fontSize: 13, lineHeight: 1.7, color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>{content}</div>
    </div>
  );
}

function LinkedInCard({ title, content, onCopy, copiedField, fieldKey, maxChars }: { title: string; content?: string; onCopy: (t: string, f: string) => void; copiedField: string | null; fieldKey: string; maxChars?: number }) {
  if (!content) return null;
  return (
    <div style={{ background: 'rgba(30,41,59,0.5)', borderRadius: 12, padding: 20, border: '1px solid rgba(14,165,233,0.3)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Linkedin size={18} color="#0ea5e9" />
          <div style={{ fontSize: 14, fontWeight: 600, color: '#e5e7eb' }}>{title}</div>
          {maxChars && (
            <span style={{ fontSize: 11, color: content.length > maxChars ? '#ef4444' : '#64748b' }}>
              {content.length}/{maxChars}
            </span>
          )}
        </div>
        <button
          onClick={() => onCopy(content, fieldKey)}
          style={{
            background: 'transparent',
            border: 'none',
            color: copiedField === fieldKey ? '#10b981' : '#64748b',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 12
          }}
        >
          {copiedField === fieldKey ? <Check size={16} /> : <Copy size={16} />}
        </button>
      </div>
      <div style={{ fontSize: 13, lineHeight: 1.7, color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>{content}</div>
    </div>
  );
}
