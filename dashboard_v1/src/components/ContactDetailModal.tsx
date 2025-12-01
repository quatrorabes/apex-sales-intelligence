import React, { useState, useEffect, useRef } from 'react';
import {
  X, Sparkles, Loader, Mail, Phone, Linkedin, Target, Lightbulb,
  PhoneCall, StickyNote, Copy, Check, Zap, FileText, User, Building2,
  Award, TrendingUp, Rocket
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
type DossierTab = 'professional' | 'company' | 'personality' | 'raw';
type ContentTab = 'email' | 'call' | 'linkedin';

export default function ContactDetailModal({ contact, onClose, onEnrichmentComplete }: ContactDetailModalProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('intelligence');
  const [activeIntelTab, setActiveIntelTab] = useState<IntelTab>('pain-points');
  const [activeDossierTab, setActiveDossierTab] = useState<DossierTab>('professional');
  const [activeContentTab, setActiveContentTab] = useState<ContentTab>('email');
  const [enriching, setEnriching] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [localContact, setLocalContact] = useState<Contact>(contact);
  const [notes, setNotes] = useState(contact.notes || '');
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [showEnrichSuccess, setShowEnrichSuccess] = useState(false);
  const [showGenerateSuccess, setShowGenerateSuccess] = useState(false);
  const [justEnriched, setJustEnriched] = useState(false);
  const [dataLoaded, setDataLoaded] = useState(false);

  const fetchedRef = useRef(false);

  const API_URL = import.meta.env.VITE_API_URL || '${import.meta.env.VITE_API_URL || "http://localhost:8000"}';

  // FIXED: Only fetch once, preserve existing profile_content
  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;

    console.log('🔄 Fetching contact:', contact.id);

    fetch(`${API_URL}/api/contacts/${contact.id}`)
      .then(res => res.json())
      .then(data => {
        console.log('📥 API returned:', { 
          id: data.id, 
          name: data.name, 
          profileLength: data.profile_content?.length || 0,
          status: data.enrichment_status 
        });

        // Only update if we got valid data
        if (data && data.id) {
          setLocalContact(data);
          setNotes(data.notes || '');
          setDataLoaded(true);
        }
      })
      .catch(err => {
        console.error('❌ Fetch failed:', err);
        setDataLoaded(true); // Still mark as loaded to show existing data
      });
  }, [contact.id, API_URL]);

  // Debug: Log whenever localContact changes
  useEffect(() => {
    console.log('📊 localContact updated:', {
      id: localContact.id,
      name: localContact.name,
      profileLength: localContact.profile_content?.length || 0,
      status: localContact.enrichment_status
    });
  }, [localContact]);

  const isEnriched = localContact.enrichment_status === 'completed' && 
                     localContact.profile_content && 
                     localContact.profile_content.length > 0;

  const hasContent = !!(localContact.email_1_subject || localContact.email_1_body || 
                       localContact.call_script_1 || localContact.linkedin_connect);

  // Simple section extraction - just by number
// ===== START: SECTION EXTRACTION FIX (Lines 45-85 approximately) =====
  
  const extractSection = (sectionNumber: number, sectionName: string): string | null => {
    if (!localContact.profile_content) return null;
    
    const content = localContact.profile_content;
    
    // Flexible patterns - section name can have additional text after it
    const patterns = [
      // Pattern 1: "## 9. Pain Points & Challenges" or "## 9. Pain Points"
      new RegExp(`##\\s+${sectionNumber}\\.\\s+${sectionName}[^\\n]*\\n([\\s\\S]*?)(?=\\n##\\s+\\d|$)`, 'i'),
      
      // Pattern 2: "## Pain Points" (no number)
      new RegExp(`##\\s+${sectionName}[^\\n]*\\n([\\s\\S]*?)(?=\\n##\\s+|$)`, 'i'),
      
      // Pattern 3: "9. Pain Points" (numbered, no ##)
      new RegExp(`${sectionNumber}\\.\\s+${sectionName}[^\\n]*\\n([\\s\\S]*?)(?=\\n\\d+\\.\\s+|$)`, 'i')
    ];
    
    for (const pattern of patterns) {
      const match = content.match(pattern);
      if (match && match[1] && match[1].trim().length > 10) {
        return match[1].trim();
      }
    }
    
    return null;
  };
  
const dossierData = {
  // Dossier Tab Sections
  overview: extractSection(1, 'Overview'),
  background: extractSection(2, 'Professional Background'),
  education: extractSection(3, 'Education'),
  personality: extractSection(6, 'Personality Detail'),
  myersBriggs: extractSection(7, 'Myers-Briggs'),
  companyOverview: extractSection(8, 'Company Overview'),
  
  // Intelligence Tab Sections (CORRECTED)
  painPoints: extractSection(9, 'Pain Points'),
  productFit: extractSection(10, 'Sales Opportunities'),  // Section 10 is "Sales Opportunities"
  keyInsights: extractSection(11, 'Key Insights'),
  finalNote: extractSection(12, 'Final Note')
};
  
  
// ===== END: SECTION EXTRACTION FIX =====
  
  const handleEnrich = async () => {
    setEnriching(true);
    setShowEnrichSuccess(false);
    setJustEnriched(false);
    try {
      console.log('🚀 Starting enrichment for:', contact.id);
      const res = await fetch(`${API_URL}/api/contacts/${contact.id}/enrich`, { method: 'POST' });
      const data = await res.json();
      console.log('📨 Enrich response:', data);

      if (data.success) {
        const updatedRes = await fetch(`${API_URL}/api/contacts/${contact.id}`);
        const updatedContact = await updatedRes.json();
        console.log('✅ Updated contact:', { profileLength: updatedContact.profile_content?.length });
        setLocalContact(updatedContact);
        onEnrichmentComplete?.(updatedContact);
        setShowEnrichSuccess(true);
        setJustEnriched(true);
        setViewMode('intelligence');
        setActiveIntelTab('pain-points');
        setTimeout(() => setShowEnrichSuccess(false), 5000);
      }
    } catch (err) {
      console.error('❌ Enrichment failed:', err);
    } finally {
      setEnriching(false);
    }
  };

  const handleGenerateContent = async () => {
    setGenerating(true);
    setShowGenerateSuccess(false);
    try {
      const res = await fetch(`${API_URL}/api/contacts/${contact.id}/generate-content`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content_type: 'all' }),
      });
      const data = await res.json();
      const updatedRes = await fetch(`${API_URL}/api/contacts/${contact.id}`);
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
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveNotes = async () => {
    try {
      await fetch(`${API_URL}/api/contacts/${contact.id}`, {
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

  // Show loading state while fetching
  if (!dataLoaded && !localContact.profile_content) {
    return (
      <div onClick={onClose} style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
        <div style={{ background: '#1e293b', borderRadius: 12, padding: 40, textAlign: 'center' }}>
          <Loader size={32} color="#6366f1" className="animate-spin" style={{ marginBottom: 16 }} />
          <div style={{ color: '#e5e7eb' }}>Loading contact data...</div>
        </div>
      </div>
    );
  }

  return (
    <div onClick={onClose} style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, padding: 20 }}>
      <div onClick={(e) => e.stopPropagation()} style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', borderRadius: 20, width: '95%', maxWidth: 1400, height: '90vh', overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.95)', border: '1px solid rgba(99,102,241,0.3)', display: 'flex', flexDirection: 'column' }}>

        {/* SUCCESS BANNER */}
        {showEnrichSuccess && (
          <div style={{ background: 'linear-gradient(135deg, #10b981, #059669)', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: 16, fontWeight: 700, color: 'white', marginBottom: 4 }}><Sparkles size={18} style={{ display: 'inline', marginRight: 8 }} />Intelligence Unlocked!</div>
              <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.9)' }}>Explore insights, personality, and company intel</div>
            </div>
            <button onClick={() => { setViewMode('outreach'); setShowEnrichSuccess(false); }} style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', border: 'none', borderRadius: 8, padding: '10px 20px', color: 'white', fontWeight: 600, cursor: 'pointer' }}>
              <Rocket size={16} style={{ display: 'inline', marginRight: 6 }} />Generate Outreach →
            </button>
          </div>
        )}

        {/* HEADER */}
        <div style={{ padding: '20px 32px', borderBottom: '1px solid rgba(148,163,184,0.2)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
              <div style={{ width: 48, height: 48, borderRadius: 999, background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: 18, fontWeight: 700 }}>
                {localContact.name?.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || '??'}
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
            <button onClick={handleEnrich} disabled={enriching} style={{ padding: '10px 20px', borderRadius: 8, border: '1px solid rgba(99,102,241,0.5)', background: enriching ? 'rgba(30,41,59,0.5)' : 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2))', color: enriching ? '#64748b' : '#a5b4fc', fontSize: 13, fontWeight: 600, cursor: enriching ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              {enriching ? <><Loader size={16} />Enriching...</> : showEnrichSuccess ? <><Check size={16} />Enriched!</> : <><Sparkles size={16} />{isEnriched ? 'Re-Enrich' : 'Enrich'}</>}
            </button>
            <button onClick={onClose} style={{ width: 40, height: 40, borderRadius: 8, border: '1px solid rgba(148,163,184,0.3)', background: 'rgba(30,41,59,0.6)', color: '#9ca3af', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><X size={20} /></button>
          </div>
        </div>

        {/* MODE TABS */}
        <div style={{ display: 'flex', borderBottom: '1px solid rgba(148,163,184,0.2)' }}>
          {[{ id: 'intelligence', label: 'Intelligence', icon: Target, badge: isEnriched ? '✓' : null }, { id: 'dossier', label: 'Dossier', icon: FileText }, { id: 'outreach', label: 'Outreach', icon: Mail, badge: hasContent ? '✓' : null }].map((mode) => {
            const Icon = mode.icon;
            return (
              <button key={mode.id} onClick={() => setViewMode(mode.id as ViewMode)} style={{ flex: 1, padding: 16, border: 'none', borderBottom: viewMode === mode.id ? '3px solid #6366f1' : '3px solid transparent', background: viewMode === mode.id ? 'rgba(99,102,241,0.1)' : 'transparent', color: viewMode === mode.id ? '#e5e7eb' : '#9ca3af', fontSize: 15, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, position: 'relative' }}>
                <Icon size={18} />{mode.label}
                {mode.badge && <span style={{ position: 'absolute', top: 8, right: 8, background: '#10b981', color: 'white', fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 999 }}>{mode.badge}</span>}
              </button>
            );
          })}
        </div>

        {/* CONTENT AREA */}
        <div style={{ flex: 1, overflow: 'auto', padding: '24px 32px' }}>

          {/* DEBUG INFO - Remove after testing */}
          <div style={{ background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.3)', borderRadius: 8, padding: 12, marginBottom: 16, fontSize: 12, color: '#fbbf24' }}>
            <strong>Debug:</strong> isEnriched={String(isEnriched)} | profile_content={localContact.profile_content?.length || 0} chars | status={localContact.enrichment_status || 'none'}
          </div>

          {viewMode === 'intelligence' && (
            <>
              <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
                {[{ id: 'pain-points', label: 'Pain Points', icon: Target }, { id: 'product-fit', label: 'Product Fit', icon: Sparkles }, { id: 'insights', label: 'Insights', icon: Lightbulb }, { id: 'call-prep', label: 'Call Prep', icon: PhoneCall }, { id: 'notes', label: 'Notes', icon: StickyNote }].map((tab) => {
                  const Icon = tab.icon;
                  return <button key={tab.id} onClick={() => setActiveIntelTab(tab.id as IntelTab)} style={{ padding: '8px 16px', borderRadius: 6, border: 'none', background: activeIntelTab === tab.id ? 'rgba(99,102,241,0.15)' : 'transparent', color: activeIntelTab === tab.id ? '#e5e7eb' : '#9ca3af', fontSize: 13, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}><Icon size={16} />{tab.label}</button>;
                })}
              </div>
              {!isEnriched ? (
                <EmptyState icon={<Sparkles size={48} color="#6366f1" />} title="Ready to Unlock Intelligence" subtitle="Click the Enrich button above to discover pain points, personality insights, and more." />
              ) : (
                <>
                  {activeIntelTab === 'pain-points' && <ContentSection title="Pain Points" content={dossierData.painPoints || localContact.profile_content?.substring(0, 2000)} icon={<Target size={20} color="#ef4444" />} />}
                  {activeIntelTab === 'product-fit' && <ContentSection title="Product Fit Analysis" content={dossierData.productFit || localContact.profile_content?.substring(0, 2000)} icon={<Sparkles size={20} color="#8b5cf6" />} />}
                  {activeIntelTab === 'insights' && <ContentSection title="Key Insights" content={dossierData.keyInsights || localContact.profile_content?.substring(0, 2000)} icon={<Lightbulb size={20} color="#fbbf24" />} />}
                  {activeIntelTab === 'call-prep' && (
                    <>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 20 }}>
                        <ScoreCard label="Priority" value={localContact.priority_score} color="#22c55e" />
                        <ScoreCard label="MDCP" value={localContact.mdcp_score} color="#eab308" />
                        <ScoreCard label="RSS" value={localContact.rss_score} color="#06b6d4" />
                      </div>
                      <ContentSection title="Call Preparation" content={dossierData.finalNote || localContact.profile_content?.substring(0, 2000)} icon={<PhoneCall size={20} color="#10b981" />} />
                    </>
                  )}
                  {activeIntelTab === 'notes' && (
                    <div>
                      <h3 style={{ fontSize: 16, fontWeight: 600, color: '#e5e7eb', marginBottom: 12 }}>Internal Notes</h3>
                      <textarea value={notes} onChange={(e) => setNotes(e.target.value)} onBlur={handleSaveNotes} placeholder="Add notes about this contact..." style={{ width: '100%', minHeight: 250, padding: 16, borderRadius: 10, border: '1px solid rgba(148,163,184,0.3)', background: 'rgba(15,23,42,0.6)', color: '#e5e7eb', fontSize: 14, lineHeight: 1.6, resize: 'vertical' }} />
                    </div>
                  )}
                </>
              )}
            </>
          )}

          {viewMode === 'dossier' && (
            <>
              <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
                {[{ id: 'professional', label: 'Professional', icon: User }, { id: 'company', label: 'Company', icon: Building2 }, { id: 'personality', label: 'Personality', icon: Award }, { id: 'raw', label: 'Raw Profile', icon: FileText }].map((tab) => {
                  const Icon = tab.icon;
                  return <button key={tab.id} onClick={() => setActiveDossierTab(tab.id as DossierTab)} style={{ padding: '8px 16px', borderRadius: 6, border: 'none', background: activeDossierTab === tab.id ? 'rgba(99,102,241,0.15)' : 'transparent', color: activeDossierTab === tab.id ? '#e5e7eb' : '#9ca3af', fontSize: 13, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}><Icon size={16} />{tab.label}</button>;
                })}
              </div>
              {!isEnriched ? (
                <EmptyState icon={<FileText size={48} color="#6366f1" />} title="No Dossier Available" subtitle="Enrich this contact first to view their full profile." />
              ) : (
                <>
                  {activeDossierTab === 'professional' && (
                    <>
                      {dossierData.overview ? <DossierCard title="Overview" content={dossierData.overview} icon={<User size={18} color="#6366f1" />} /> : null}
                      {dossierData.background ? <DossierCard title="Background" content={dossierData.background} icon={<TrendingUp size={18} color="#8b5cf6" />} /> : null}
                      {dossierData.education ? <DossierCard title="Education" content={dossierData.education} icon={<Award size={18} color="#10b981" />} /> : null}
                      {/* Fallback: show raw profile if no sections parsed */}
                      {!dossierData.overview && !dossierData.background && localContact.profile_content && (
                        <DossierCard title="Full Profile" content={localContact.profile_content} icon={<FileText size={18} color="#6366f1" />} />
                      )}
                    </>
                  )}
                  {activeDossierTab === 'company' && (
                    <>
                      {dossierData.companyOverview ? <DossierCard title="Company Overview" content={dossierData.companyOverview} icon={<Building2 size={18} color="#0ea5e9" />} /> : <DossierCard title="Full Profile" content={localContact.profile_content} icon={<FileText size={18} color="#0ea5e9" />} />}
                    </>
                  )}
                  {activeDossierTab === 'personality' && (
                    <>
                      {dossierData.personality ? <DossierCard title="Personality Traits" content={dossierData.personality} icon={<Award size={18} color="#f59e0b" />} /> : null}
                      {dossierData.myersBriggs ? <DossierCard title="Myers-Briggs Type" content={dossierData.myersBriggs} icon={<Lightbulb size={18} color="#8b5cf6" />} /> : null}
                      {!dossierData.personality && !dossierData.myersBriggs && localContact.profile_content && (
                        <DossierCard title="Full Profile" content={localContact.profile_content} icon={<FileText size={18} color="#6366f1" />} />
                      )}
                    </>
                  )}
                  {activeDossierTab === 'raw' && (
                    <div style={{ background: 'rgba(30,41,59,0.5)', borderRadius: 12, padding: 20, border: '1px solid rgba(148,163,184,0.2)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                        <FileText size={18} color="#6366f1" />
                        <h3 style={{ fontSize: 16, fontWeight: 600, color: '#e5e7eb' }}>Full Profile ({localContact.profile_content?.length || 0} chars)</h3>
                      </div>
                      <div style={{ fontSize: 13, lineHeight: 1.7, color: '#cbd5e1', whiteSpace: 'pre-wrap', maxHeight: '60vh', overflow: 'auto' }}>{localContact.profile_content || 'No profile content available'}</div>
                    </div>
                  )}
                </>
              )}
            </>
          )}

          {viewMode === 'outreach' && (
            <>
              <div style={{ display: 'flex', gap: 12, marginBottom: 20, alignItems: 'center' }}>
                {[{ id: 'email', label: 'Email', icon: Mail, color: '#6366f1' }, { id: 'call', label: 'Call Scripts', icon: PhoneCall, color: '#10b981' }, { id: 'linkedin', label: 'LinkedIn', icon: Linkedin, color: '#0ea5e9' }].map((tab) => {
                  const Icon = tab.icon;
                  return <button key={tab.id} onClick={() => setActiveContentTab(tab.id as ContentTab)} style={{ padding: '10px 20px', borderRadius: 8, border: activeContentTab === tab.id ? `1px solid ${tab.color}` : '1px solid transparent', background: activeContentTab === tab.id ? `${tab.color}15` : 'transparent', color: activeContentTab === tab.id ? tab.color : '#9ca3af', fontSize: 13, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}><Icon size={16} />{tab.label}</button>;
                })}
                <button onClick={handleGenerateContent} disabled={generating} style={{ marginLeft: 'auto', padding: '10px 16px', borderRadius: 8, border: 'none', background: generating ? 'rgba(71,85,105,0.5)' : 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', fontSize: 12, fontWeight: 600, cursor: generating ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
                  {generating ? <><Loader size={14} />Generating...</> : <><Zap size={14} />Generate All Content</>}
                </button>
              </div>
              {!isEnriched ? <EmptyState icon={<Sparkles size={48} color="#6366f1" />} title="Enrich First" subtitle="Generate intelligence before creating outreach content." />
              : !hasContent ? <EmptyState icon={<Rocket size={48} color="#8b5cf6" />} title="Ready to Generate" subtitle="Click Generate All Content to create personalized emails, call scripts, and LinkedIn messages." />
              : (
                <>
                  {activeContentTab === 'email' && <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>{[1, 2, 3].map((num) => { const subject = localContact[`email_${num}_subject` as keyof Contact] as string; const body = localContact[`email_${num}_body` as keyof Contact] as string; if (!subject && !body) return null; return <EmailCard key={num} number={num} subject={subject || ''} body={body || ''} onCopy={copyToClipboard} copiedField={copiedField} />; })}</div>}
                  {activeContentTab === 'call' && <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>{[1, 2, 3].map((num) => { const script = localContact[`call_script_${num}` as keyof Contact] as string; if (!script) return null; const labels = ['Direct & Value-Focused', 'Consultative', 'Executive']; return <CallScriptCard key={num} number={num} label={labels[num - 1]} content={script} onCopy={copyToClipboard} copiedField={copiedField} />; })}</div>}
                  {activeContentTab === 'linkedin' && <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}><LinkedInCard title="Connection Request" content={localContact.linkedin_connect} onCopy={copyToClipboard} copiedField={copiedField} fieldKey="linkedin_connect" /></div>}
                </>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// HELPER COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════

function StatusBadge({ contact }: { contact: Contact }) {
  const baseStyle = {
    padding: '4px 10px',
    borderRadius: 999,
    fontSize: 11,
    fontWeight: 700
  };

  if (contact.call_script_1 || contact.email_1_body || contact.linkedin_connect) {
    return (
      <span style={{ ...baseStyle, background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.5)', color: '#10b981' }}>
        ✍️ Content Ready
      </span>
    );
  }
  if (contact.priority_score) {
    return (
      <span style={{ ...baseStyle, background: 'rgba(251,191,36,0.15)', border: '1px solid rgba(251,191,36,0.5)', color: '#fbbf24' }}>
        🎯 Scored
      </span>
    );
  }
  if (contact.enrichment_status === 'completed') {
    return (
      <span style={{ ...baseStyle, background: 'rgba(139,92,246,0.15)', border: '1px solid rgba(139,92,246,0.5)', color: '#8b5cf6' }}>
        ✨ Enriched
      </span>
    );
  }
  return (
    <span style={{ ...baseStyle, background: 'rgba(71,85,105,0.15)', border: '1px solid rgba(71,85,105,0.5)', color: '#64748b' }}>
      ○ Pending
    </span>
  );
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
  // Clean markdown from content
  const cleanContent = content
    ?.replace(/^###\s+[\d.]+\s*/gm, '')     // Remove ### 8.1. style headers
    ?.replace(/^##\s+[\d.]+\s*/gm, '')      // Remove ## 8. style headers
    ?.replace(/^##\s+/gm, '')               // Remove remaining ##
    ?.replace(/^###\s+/gm, '')              // Remove remaining ###
    ?.replace(/\*\*(.+?)\*\*/g, '$1')       // Remove bold markers
    ?.replace(/^- \*\*(.+?)\*\*/gm, '• $1') // Convert list bold to bullet
    ?.replace(/^- /gm, '• ')                // Convert dashes to bullets
    ?.replace(/\n{3,}/g, '\n\n')            // Clean up extra newlines
    ?.trim();

  return (
    <div style={{
      background: 'rgba(30,41,59,0.5)',
      borderRadius: 12,
      padding: 20,
      border: '1px solid rgba(148,163,184,0.2)',
      marginBottom: 16
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        {icon}
        <h3 style={{ fontSize: 16, fontWeight: 600, color: '#e5e7eb', margin: 0 }}>{title}</h3>
      </div>
      <div style={{ fontSize: 14, lineHeight: 1.7, color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>
        {cleanContent || 'No data available'}
      </div>
    </div>
  );
}

function DossierCard({ title, content, icon }: { title: string; content?: string | null; icon?: React.ReactNode }) {
  if (!content) return null;
  
  // Clean markdown from content
  const cleanContent = content
    ?.replace(/^###\s+[\d.]+\s*/gm, '')
    ?.replace(/^##\s+[\d.]+\s*/gm, '')
    ?.replace(/^##\s+/gm, '')
    ?.replace(/^###\s+/gm, '')
    ?.replace(/\*\*(.+?)\*\*/g, '$1')
    ?.replace(/^- /gm, '• ')
    ?.replace(/\n{3,}/g, '\n\n')
    ?.trim();

  return (
    <div style={{
      background: 'rgba(30,41,59,0.5)',
      borderRadius: 12,
      padding: 20,
      border: '1px solid rgba(148,163,184,0.2)',
      marginBottom: 16
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        {icon}
        <h3 style={{ fontSize: 16, fontWeight: 600, color: '#e5e7eb', margin: 0 }}>{title}</h3>
      </div>
      <div style={{ fontSize: 14, lineHeight: 1.7, color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>
        {cleanContent}
      </div>
    </div>
  );
}

function ScoreCard({ label, value, color }: { label: string; value?: number; color: string }) {
  return (
    <div style={{
      background: 'rgba(30,41,59,0.5)',
      borderRadius: 12,
      padding: 20,
      border: '1px solid rgba(148,163,184,0.2)',
      textAlign: 'center'
    }}>
      <div style={{ fontSize: 12, color: '#9ca3af', marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: 32, fontWeight: 700, color }}>
        {value != null ? Math.round(value) : '—'}
      </div>
    </div>
  );
}

function EmailCard({ number, subject, body, onCopy, copiedField }: { 
  number: number; 
  subject: string; 
  body: string; 
  onCopy: (t: string, f: string) => void; 
  copiedField: string | null 
}) {
  const labels = ['Initial Outreach', 'Follow-up', 'Break-up'];
  const colors = ['#6366f1', '#8b5cf6', '#a855f7'];
  const color = colors[number - 1];

  return (
    <div style={{
      background: 'rgba(30,41,59,0.5)',
      borderRadius: 12,
      padding: 20,
      border: `1px solid ${color}30`
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 600, color }}>Email {number}</div>
          <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 4 }}>{labels[number - 1]}</div>
        </div>
        <button
          onClick={() => onCopy(`Subject: ${subject}\n\n${body}`, `email_${number}`)}
          style={{ background: 'transparent', border: 'none', color: copiedField === `email_${number}` ? '#10b981' : '#64748b', cursor: 'pointer' }}
        >
          {copiedField === `email_${number}` ? <Check size={16} /> : <Copy size={16} />}
        </button>
      </div>
      <div style={{ marginBottom: 8 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: '#9ca3af' }}>SUBJECT</div>
        <div style={{ fontSize: 13, color: '#e5e7eb' }}>{subject}</div>
      </div>
      <div>
        <div style={{ fontSize: 11, fontWeight: 600, color: '#9ca3af' }}>BODY</div>
        <div style={{ fontSize: 13, lineHeight: 1.6, color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>{body}</div>
      </div>
    </div>
  );
}

function CallScriptCard({ number, label, content, onCopy, copiedField }: { 
  number: number; 
  label: string; 
  content: string; 
  onCopy: (t: string, f: string) => void; 
  copiedField: string | null 
}) {
  const colors = ['#10b981', '#22c55e', '#16a34a'];
  const color = colors[number - 1];

  return (
    <div style={{
      background: 'rgba(30,41,59,0.5)',
      borderRadius: 12,
      padding: 20,
      border: `1px solid ${color}30`
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 600, color }}>Script {number}</div>
          <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 4 }}>{label}</div>
        </div>
        <button
          onClick={() => onCopy(content, `call_${number}`)}
          style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer' }}
        >
          <Copy size={16} />
        </button>
      </div>
      <div style={{ fontSize: 13, lineHeight: 1.6, color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>{content}</div>
    </div>
  );
}

function LinkedInCard({ title, content, onCopy, copiedField, fieldKey }: { 
  title: string; 
  content?: string; 
  onCopy: (t: string, f: string) => void; 
  copiedField: string | null; 
  fieldKey: string 
}) {
  if (!content) return null;

  return (
    <div style={{
      background: 'rgba(30,41,59,0.5)',
      borderRadius: 12,
      padding: 20,
      border: '1px solid rgba(14,165,233,0.3)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Linkedin size={18} color="#0ea5e9" />
          <div style={{ fontSize: 14, fontWeight: 600, color: '#e5e7eb' }}>{title}</div>
        </div>
        <button
          onClick={() => onCopy(content, fieldKey)}
          style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer' }}
        >
          <Copy size={16} />
        </button>
      </div>
      <div style={{ fontSize: 13, lineHeight: 1.6, color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>{content}</div>
    </div>
  );
}
