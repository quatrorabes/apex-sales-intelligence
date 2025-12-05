import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import TodaysBoard from './components/TodaysBoard';
import ContactsView from './components/ContactsView';
import ContactDetail from './components/ContactDetail';
import ColdCallQueue from './components/ColdCallQueue';
import Analytics from './components/Analytics';
import SmartLists from './components/SmartLists';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/board" element={<TodaysBoard />} />
                <Route path="/contacts" element={<ContactsView />} />
                <Route path="/contacts/:id" element={<ContactDetail />} />
                <Route path="/cold-call" element={<ColdCallQueue />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/smart-lists" element={<SmartLists />} />
            </Routes>
        </Router>
    );
}

export default App;
