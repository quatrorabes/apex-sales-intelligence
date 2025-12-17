import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';

import AppShell from './layouts/AppShell';
import LandingPage from './components/LandingPage';
import TodaysBoard from './components/TodaysBoard';
import ContactsView from './components/ContactsView';
import ContactDetailPage from './pages/ContactDetailPage';

function App() {
  return (
    <MantineProvider>
      <Notifications position="top-right" />
      <Router>
        <Routes>
          <Route path="/" element={<AppShell />}>
            <Route index element={<LandingPage />} />
            <Route path="dashboard" element={<TodaysBoard />} />
            <Route path="todays-board" element={<TodaysBoard />} />
            <Route path="contacts" element={<ContactsView />} />
            <Route path="contacts/:id" element={<ContactDetailPage />} />
          </Route>
        </Routes>
      </Router>
    </MantineProvider>
  );
}

export default App;
