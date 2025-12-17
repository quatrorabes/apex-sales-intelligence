import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { config } from '../config';
import '../styles/ContactDetail.css';

interface Contact {
  id: string;
  name: string;
  email: string;
  company: string;
  title: string;
  phone?: string;
  linkedin_url?: string;
  enrichment_status?: string;
  enrichment_data?: any;
  mdcp_score?: number;
  rss_score?: number;
  unified_qualification_score?: number;
}

export default function ContactDetail() {
  const { contactId } = useParams<{ contactId: string }>();
  const navigate = useNavigate();
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [generatedEmail, setGeneratedEmail] = useState<string | null>(null);
  const [generatedCall, setGeneratedCall] = useState<string | null>(null);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [showCallModal, setShowCallModal] = useState(false);

  useEffect(() => {
    if (contactId) fetchContact();
  }, [contactId]);

  const fetchContact = async () => {
    if (!contactId) return;
    try {
      setLoading(true);
      const url = `${config.API_BASE_URL}/api/contacts/${contactId}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Contact not found');
      
      const data = await response.json();
      setContact(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const triggerEnrichment = async () => {
    if (!contactId) return;
    
    try {
      setEnriching(true);
      setError(null);
      const url = `${config.API_BASE_URL}/api/v2/contacts/${contactId}/enrich`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) throw new Error('Enrichment failed');
      
      // Poll for completion
      let completed = false;
      let attempts = 0;
      
      while (!completed && attempts < 180) {
        await new Promise(r => setTimeout(r, 2000));
        
        const statusUrl = `${config.API_BASE_URL}/api/v2/contacts/${contactId}/enrichment-status`;
        const statusResponse = await fetch(statusUrl);
        
        if (!statusResponse.ok) {
          attempts++;
          continue;
        }
        
        const statusData = await statusResponse.json();
        
        if (statusData.enrichment_status === 'completed') {
          completed = true;
          await new Promise(r => setTimeout(r, 500));
          await fetchContact();
        }
        attempts++;
      }
      
      if (!completed) setError('Enrichment timed out');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Enrichment failed');
    } finally {
      setEnriching(false);
    }
  };

  const generateEmail = async () => {
    if (!contactId || !contact?.enrichment_data) {
      setError('Contact not enriched');
      return;
    }
    
    try {
      const url = `${config.API_BASE_URL}/api/contacts/${contactId}/generate-email`;
      const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
      if (!response.ok) throw new Error('Failed to generate email');
      const data = await response.json();
      setGeneratedEmail(data.email);
      setShowEmailModal(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
    }
  };

  const generateCallScript = async () => {
    if (!contactId || !contact?.enrichment_data) {
      setError('Contact not enriched');
      return;
    }
    
    try {
      const url = `${config.API_BASE_URL}/api/contacts/${contactId}/generate-call-script`;
      const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
      if (!response.ok) throw new Error('Failed to generate script');
      const data = await response.json();
      setGeneratedCall(data.script);
      setShowCallModal(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
    }
  };

  const parseEnrichmentData = (data: any) => {
    if (!data) return {};
    if (typeof data === 'string') {
      try {
        data = JSON.parse(data);
      } catch {
        return {};
      }
    }
    return data;
  };

  if (loading) return <div className="loading">Loading contact...</div>;
  if (error && !contact) return <div className="error">{error} <button onClick={() => navigate('/')}>Back</button></div>;
  if (!contact) return <div className="error">Contact not found</div>;

  const enrichmentData = parseEnrichmentData(contact.enrichment_data);
  const isEnriched = contact.enrichment_status === 'completed' && enrichmentData.markdown;

  return (
    <div className="contact-detail">
      <button className="back-button" onClick={() => navigate('/')}>← Back</button>
      
      <header className="detail-header">
        <div className="header-content">
          <h1>{contact.name}</h1>
          <p className="subtitle">{contact.title} at {contact.company}</p>
        </div>
        <div className="header-actions">
          <button 
            className="btn btn-primary"
            onClick={triggerEnrichment}
            disabled={enriching || isEnriched}
          >
            {enriching ? 'Enriching...' : isEnriched ? '✓ Enriched' : 'Enrich'}
          </button>
        </div>
      </header>

      {isEnriched && (
        <div className="action-buttons">
          <button className="btn btn-secondary" onClick={generateEmail}>📧 Email</button>
          <button className="btn btn-secondary" onClick={generateCallScript}>☎️ Call Script</button>
        </div>
      )}

      <div className="detail-scores">
        {contact.mdcp_score && <div className="score-card"><label>MDCP</label><value>{Math.round(contact.mdcp_score)}</value></div>}
        {contact.rss_score && <div className="score-card"><label>RSS</label><value>{Math.round(contact.rss_score)}</value></div>}
        {contact.unified_qualification_score && <div className="score-card highlight"><label>Score</label><value>{Math.round(contact.unified_qualification_score)}</value></div>}
      </div>

      <div className="detail-tabs">
        <button className={`tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>Overview</button>
        {isEnriched && <button className={`tab ${activeTab === 'enrichment' ? 'active' : ''}`} onClick={() => setActiveTab('enrichment')}>Enrichment</button>}
      </div>

      <div className="detail-content">
        {activeTab === 'overview' && (
          <div className="overview-panel">
            <div className="info-group"><label>Email</label><p>{contact.email || 'N/A'}</p></div>
            <div className="info-group"><label>Phone</label><p>{contact.phone || 'N/A'}</p></div>
            <div className="info-group"><label>LinkedIn</label><p>{contact.linkedin_url ? <a href={contact.linkedin_url} target="_blank" rel="noopener">View</a> : 'N/A'}</p></div>
            <div className="info-group"><label>Status</label><p className={`status-badge ${contact.enrichment_status}`}>{contact.enrichment_status}</p></div>
          </div>
        )}

        {activeTab === 'enrichment' && isEnriched && (
          <div className="enrichment-panel">
            <div className="enrichment-meta">Enriched: {new Date(enrichmentData.enriched_at).toLocaleString()}</div>
            <div className="enrichment-markdown">{enrichmentData.markdown}</div>
          </div>
        )}
      </div>

      {showEmailModal && (
        <div className="modal" onClick={() => setShowEmailModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Generated Email</h3>
            <textarea value={generatedEmail || ''} readOnly rows={12}></textarea>
            <button onClick={() => {navigator.clipboard.writeText(generatedEmail || ''); alert('Copied!');}} className="btn btn-primary">Copy</button>
            <button onClick={() => setShowEmailModal(false)} className="btn btn-secondary">Close</button>
          </div>
        </div>
      )}

      {showCallModal && (
        <div className="modal" onClick={() => setShowCallModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Call Script</h3>
            <textarea value={generatedCall || ''} readOnly rows={12}></textarea>
            <button onClick={() => {navigator.clipboard.writeText(generatedCall || ''); alert('Copied!');}} className="btn btn-primary">Copy</button>
            <button onClick={() => setShowCallModal(false)} className="btn btn-secondary">Close</button>
          </div>
        </div>
      )}

      {error && <div className="error-banner">{error}</div>}
    </div>
  );
}
