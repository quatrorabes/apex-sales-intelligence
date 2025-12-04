import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeDemo } from './pages/ThemeDemo';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/demo" element={<ThemeDemo />} />
        <Route path="/" element={
          <div className="min-h-screen bg-midnight-950 flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-text-primary mb-4">
                APEX Sales Intelligence
              </h1>
              <p className="text-text-secondary mb-6">Warm Midnight Theme Active</p>
              <a 
                href="/demo" 
                className="inline-block bg-gradient-to-r from-gold to-gold-hover text-midnight-950 font-semibold px-8 py-4 rounded-xl hover:shadow-gold-glow transition-all"
              >
                View Theme Demo
              </a>
            </div>
          </div>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;