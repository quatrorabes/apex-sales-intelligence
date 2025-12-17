import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ContactDetail from './components/ContactDetail';
import ContactsList from './components/ContactsList';
import './App.css';

function HomePage() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>🚀 APEX Sales Intelligence</h1>
        <p className="subtitle">Unified sales qualification and enrichment platform</p>
      </header>

      <main className="app-main">
        <ContactsList />
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/contacts/:contactId" element={<ContactDetail />} />
      </Routes>
    </Router>
  );
}

export default App;
