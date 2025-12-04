import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeDemo } from './pages/ThemeDemo';
import TodaysBoard from './components/TodaysBoard';
import ContactDetail from './pages/ContactDetail';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/todays-board" element={<TodaysBoard />} />
        <Route path="/contacts/:id" element={<ContactDetail />} />
        <Route path="/demo" element={<ThemeDemo />} />
        <Route path="/" element={
          <div className="min-h-screen bg-midnight-950 flex items-center justify-center">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-text-primary mb-4">
                APEX Sales Intelligence
              </h1>
              <p className="text-text-secondary mb-6">Warm Midnight Theme Active</p>
              <div className="flex gap-4 justify-center">
                <a 
                  href="/todays-board" 
                  className="inline-block bg-gradient-to-r from-gold to-gold-hover text-midnight-950 font-semibold px-8 py-4 rounded-xl hover:shadow-gold-glow transition-all"
                >
                  📋 Today's Board
                </a>
                <a 
                  href="/demo" 
                  className="inline-block bg-midnight-800 text-text-primary font-semibold px-8 py-4 rounded-xl hover:bg-midnight-700 transition-all border border-midnight-600"
                >
                  🎨 Theme Demo
                </a>
              </div>
            </div>
          </div>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;