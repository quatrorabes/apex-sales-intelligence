import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
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

interface EnrichmentData {
  markdown?: string;
  raw_context?: Record<string, string>;
  enriched_at?: string;
}

export default function ContactDetail() {
  const { contactId } = useParams<{ contactId: string }>();
  const [contact, setContact] = useState<Contact | null>(null);
  const [enrichmentData, setEnrichmentData] = useState<EnrichmentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  const API_URL = process.env.REACT_APP_API_URL || 'https://apex-backend-i7b0.onrender.com';

  useEffect(() => {
    fetchContact();
  }, [contactId]);

  const fetchContact = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/contacts/${contactId}`);
      if (!response.ok) throw new Error('Failed to fetch contact');
      
      const data = await response.json();
      setContact(data);
      
      if (data.enrichment_data) {
        try {
          const enrichData = typeof data.enrichment_data === 'string' 
            ? JSON.parse(data.enrichment_data) 
            : data.enrichment_data;
          setEnrichmentData(enrichData);
        } catch (e) {
          console.error('Failed to parse enrichment data:', e);
        }
      }
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
      const response = await fetch(`${API_URL}/api/v2/contacts/${contactId}/enrich`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) throw new Error('Enrichment failed');
      
      let completed = false;
      let attempts = 0;
      
      while (!completed && attempts < 120) {
        await new Promise(r => setTimeout(r, 2000));
        
        const statusResponse = await fetch(
          `${API_URL}/api/v2/contacts/${contactId}/enrichment-status`
        );
        const statusData = await statusResponse.json();
        
        if (statusData.enrichment_status === 'completed') {
          completed = true;
          await fetchContact();
        }
        attempts++;
      }
      
      if (!completed) {
        setError('Enrichment timeout - please check back later');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Enrichment failed');
    } finally {
      setEnriching(false);
    }
  };

  const parseMarkdownSections = (markdown: string): Record<string, string> => {
    const sections: Record<string, string> = {};
    const parts = markdown.split(/^## /m);
    
    for (const part of parts) {
      if (!part.trim()) continue;
      const lines = part.split('\n');
      const header = lines[0].trim()
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '_')
        .replace(/^_|_$/g, '');
      const content = lines.slice(1).join('\n').trim();
      if (header && content) sections[header] = content;
    }
    
    return sections;
  };

  if (loading) return <div className="loading">Loading contact...</div>;
  if (error && !contact) return <div className="error">Error: {error}</div>;
  if (!contact) return <div className="error">Contact not found</div>;

  const enrichedSections = enrichmentData?.markdown 
    ? parseMarkdownSections(enrichmentData.markdown)
    : {};

  return (
    <div className="contact-detail">
      <header className="detail-header">
        <div className="header-content">
          <h1>{contact.name}</h1>
          <p className="subtitle">{contact.title} at {contact.company}</p>
        </div>
        <div className="header-actions">
          {contact.enrichment_status !== 'completed' && (
            <button 
              className="enrich-btn"
              onClick={triggerEnrichment}
              disabled={enriching}
            >
              {enriching ? 'Enriching...' : '✨ Enrich Contact'}
            </button>
          )}
        </div>
      </header>

      <div className="detail-scores">
        {contact.mdcp_score && (
          <div className="score-card">
            <div className="score-label">MDCP Score</div>
            <div className="score-value">{Math.round(contact.mdcp_score)}</div>
          </div>
        )}
        {contact.rss_score && (
          <div className="score-card">
            <div className="score-label">RSS Score</div>
            <div className="score-value">{Math.round(contact.rss_score)}</div>
          </div>
        )}
        {contact.unified_qualification_score && (
          <div className="score-card highlight">
            <div className="score-label">Unified Score</div>
            <div className="score-value">{Math.round(contact.unified_qualification_score)}</div>
          </div>
        )}
      </div>

      <div className="detail-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'enrichment' ? 'active' : ''}`}
          onClick={() => setActiveTab('enrichment')}
        >
          Enrichment
        </button>
      </div>

      <div className="detail-content">
        {activeTab === 'overview' && (
          <div className="overview-panel">
            <div className="info-group">
              <label>Email</label>
              <p>{contact.email}</p>
            </div>
            <div className="info-group">
              <label>Phone</label>
              <p>{contact.phone || 'Not provided'}</p>
            </div>
            <div className="info-group">
              <label>LinkedIn</label>
              {contact.linkedin_url ? (
                <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer">
                  {contact.linkedin_url}
                </a>
              ) : (
                <p>Not provided</p>
              )}
            </div>
            <div className="info-group">
              <label>Enrichment Status</label>
              <p className={`status ${contact.enrichment_status}`}>
                {contact.enrichment_status || 'Pending'}
              </p>
            </div>
          </div>
        )}

        {activeTab === 'enrichment' && (
          <div className="enrichment-panel">
            {enrichmentData?.markdown ? (
              <>
                <div className="enrichment-meta">
                  Enriched: {enrichmentData.enriched_at ? new Date(enrichmentData.enriched_at).toLocaleString() : 'Unknown'}
                </div>
                
                {Object.entries(enrichedSections).map(([section, content]) => (
                  <div key={section} className="enrichment-section">
                    <h3>{section.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</h3>
                    <div className="section-content">
                      {content.split('\n').map((line, i) => (
                        <p key={i}>{line}</p>
                      ))}
                    </div>
                  </div>
                ))}
              </>
            ) : (
              <div className="empty-state">
                <p>No enrichment data available</p>
                <p className="hint">Click "Enrich Contact" to generate intelligence</p>
              </div>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="error-banner">{error}</div>
      )}
    </div>
  );
}
