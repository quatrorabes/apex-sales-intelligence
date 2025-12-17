import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { config } from '../config';
import '../styles/ContactsList.css';

interface Contact {
  id: string;
  name: string;
  title: string;
  company: string;
  email?: string;
  mdcp_score?: number;
  unified_qualification_score?: number;
  enrichment_status?: string;
}

export default function ContactsList() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState('name');

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    try {
      setLoading(true);
      const url = `${config.API_BASE_URL}${config.API_ENDPOINTS.CONTACTS}?limit=100&offset=0`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch contacts');
      
      const data = await response.json();
      const contactsList = Array.isArray(data) ? data : data.contacts || [];
      setContacts(contactsList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const getSortedContacts = () => {
    const sorted = [...contacts];
    switch(sortBy) {
      case 'score':
        return sorted.sort((a, b) => (b.unified_qualification_score || 0) - (a.unified_qualification_score || 0));
      case 'enriched':
        return sorted.sort((a, b) => {
          const aEnriched = a.enrichment_status === 'completed' ? 1 : 0;
          const bEnriched = b.enrichment_status === 'completed' ? 1 : 0;
          return bEnriched - aEnriched;
        });
      default:
        return sorted.sort((a, b) => a.name.localeCompare(b.name));
    }
  };

  const enrichedCount = contacts.filter(c => c.enrichment_status === 'completed').length;
  const avgScore = contacts.reduce((sum, c) => sum + (c.unified_qualification_score || 0), 0) / contacts.length || 0;

  return (
    <div className="contacts-list">
      <div className="list-header">
        <h2>All Contacts</h2>
        <div className="list-stats">
          <div className="stat">
            <span className="stat-label">Total</span>
            <span className="stat-value">{contacts.length}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Enriched</span>
            <span className="stat-value">{enrichedCount}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Avg Score</span>
            <span className="stat-value">{Math.round(avgScore)}</span>
          </div>
        </div>
      </div>

      <div className="list-controls">
        <label>Sort by:</label>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="name">Name (A-Z)</option>
          <option value="score">Score (High-Low)</option>
          <option value="enriched">Enrichment Status</option>
        </select>
      </div>

      {error && <div className="error-message">{error}</div>}
      {loading && <div className="loading">Loading contacts...</div>}

      {!loading && contacts.length > 0 && (
        <div className="list-table">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Title</th>
                <th>Company</th>
                <th>Score</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {getSortedContacts().map(contact => (
                <tr key={contact.id} className={`status-${contact.enrichment_status}`}>
                  <td className="name-col">{contact.name}</td>
                  <td className="title-col">{contact.title}</td>
                  <td className="company-col">{contact.company}</td>
                  <td className="score-col">
                    {contact.unified_qualification_score ? (
                      <span className="score-badge">
                        {Math.round(contact.unified_qualification_score)}
                      </span>
                    ) : (
                      <span className="score-badge empty">—</span>
                    )}
                  </td>
                  <td className="status-col">
                    <span className={`status-badge ${contact.enrichment_status}`}>
                      {contact.enrichment_status === 'completed' ? '✓ Enriched' : 'Pending'}
                    </span>
                  </td>
                  <td className="action-col">
                    <Link to={`/contacts/${contact.id}`} className="view-link">
                      View →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && contacts.length === 0 && (
        <div className="empty-state">
          <p>No contacts found</p>
        </div>
      )}
    </div>
  );
}
