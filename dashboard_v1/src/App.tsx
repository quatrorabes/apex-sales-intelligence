import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ContactDetail from './components/ContactDetail';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/contacts/:contactId" element={<ContactDetail />} />
        <Route path="/" element={
          <div className="app">
            <header className="app-header">
              <h1>APEX Sales Intelligence</h1>
              <p>Unified sales qualification and enrichment platform</p>
            </header>
            <main className="app-main">
              <p>Navigate to /contacts/:contactId to view contact details</p>
            </main>
          </div>
        } />
      </Routes>
    </Router>
  );
}

export default App;
