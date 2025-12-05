import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppShell } from './layouts/AppShell';
import { ThemeDemo } from './pages/ThemeDemo';
import TodaysBoard from './components/TodaysBoard';
import ContactDetail from './components/ContactDetail';
import Contacts from './pages/Contacts';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<TodaysBoard />} />
          <Route path="/todays-board" element={<TodaysBoard />} />
          <Route path="/contacts" element={<Contacts />} />
          <Route path="/contacts/:id" element={<ContactDetail />} />
          <Route path="/demo" element={<ThemeDemo />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}

export default App;
