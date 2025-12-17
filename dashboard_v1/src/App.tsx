import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import ContactsView from './components/ContactsView';
import ContactDetail from './components/ContactDetail';
import TodaysBoard from './components/TodaysBoard';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/contacts" element={<ContactsView />} />
          <Route path="/contacts/:contactId" element={<ContactDetail />} />
          <Route path="/today" element={<TodaysBoard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
