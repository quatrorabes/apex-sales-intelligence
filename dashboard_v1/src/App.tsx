import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import TodaysBoard from './components/TodaysBoard';
import ContactsView from './components/ContactsView';
import ContactDetail from './pages/ContactDetailPage';
import CallAssistantPage from './pages/CallAssistantPage';
import Analytics from './components/Analytics';
import ColdCallQueue from './components/ColdCallQueue';
import SmartLists from './components/SmartLists';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/board" element={<TodaysBoard />} />
        <Route path="/todays-board" element={<TodaysBoard />} />
        <Route path="/contacts" element={<ContactsView />} />
        <Route path="/contacts/:id" element={<ContactDetail />} />
        <Route path="/contacts/:id/call-assistant" element={<CallAssistantPage />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/cold-call" element={<ColdCallQueue />} />
        <Route path="/smart-lists" element={<SmartLists />} />
      </Routes>
    </Router>
  );
}

export default App;
