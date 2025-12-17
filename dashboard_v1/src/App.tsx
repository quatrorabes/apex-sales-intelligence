import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ContactDetail from './components/ContactDetail';
import { config } from './config';
import './App.css';

interface Contact {
  id: string;
  name: string;
  title: string;
  company: string;
  email?: string;
}

function LandingPage() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    try {
      setLoading(true);
      const url = `${config.API_BASE_URL}${config.API_ENDPOINTS.CONTACTS}?limit=50&offset=0`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch contacts');
      
      const data = await response.json();
      setContacts(Array.isArray(data) ? data : data.contacts || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚀 APEX Sales Intelligence</h1>
        <p className="subtitle">Unified sales qualification and enrichment platform</p>
      </header>

      <main className="app-main">
        {error && <div className="error-message">{error}</div>}
        
        {loading && <div className="loading">Loading contacts...</div>}
        
        {!loading && contacts.length > 0 && (
          <div className="contacts-section">
            <h2>Contacts ({contacts.length})</h2>
            <div className="contacts-grid">
              {contacts.map(contact => (
                <Link 
                  key={contact.id} 
                  to={`/contacts/${contact.id}`}
                  className="contact-card"
                >
                  <div className="contact-card-header">
                    <h3>{contact.name}</h3>
                    <p className="contact-title">{contact.title}</p>
                  </div>
                  <div className="contact-card-body">
                    <p className="contact-company">{contact.company}</p>
                    {contact.email && <p className="contact-email">{contact.email}</p>}
                  </div>
                  <div className="contact-card-footer">
                    <span className="view-detail">View Details →</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
        
        {!loading && contacts.length === 0 && (
          <div className="empty-state">
            <p>No contacts found</p>
          </div>
        )}
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/contacts/:contactId" element={<ContactDetail />} />
      </Routes>
    </Router>
  );
}

export default App;
