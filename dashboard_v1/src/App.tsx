import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { TodaysBoard } from './components/TodaysBoard';
import { ContactDetailPage } from './pages/ContactDetailPage';
// import { AllContactsView } from './pages/AllContactsView'; // If you have this

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-900">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<TodaysBoard />} />
          {/* <Route path="/contacts" element={<AllContactsView />} /> */}
          <Route path="/contacts/:id" element={<ContactDetailPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
