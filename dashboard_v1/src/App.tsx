import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import TodaysBoard from './components/TodaysBoard';
import ContactsView from './components/ContactsView';
import ContactDetail from './pages/ContactDetail';

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Routes>
          <Route path="/" element={<Navigate to="/todays-board" replace />} />
          <Route path="/todays-board" element={<TodaysBoard />} />
          <Route path="/contacts" element={<ContactsView />} />
          <Route path="/contacts/:id" element={<ContactDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
