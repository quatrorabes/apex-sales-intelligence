import React, { useState, useEffect } from 'react';
import { Home, Users, Calendar, Brain, Sparkles, BarChart3, Menu, X } from 'lucide-react';
import TodaysBoard from './components/TodaysBoard';
import ContactsBoard from './components/ContactsBoard';
import ApexIntelligence from './components/ApexIntelligence';
import ContactEnrichmentView from './components/ContactEnrichmentView';
import CadenceDashboard from './components/CadenceDashboard';
import { OnboardingModal } from './components/OnboardingModal';
import { apiClient } from './utils/api';
import './styles/index.css';

type View = 'today' | 'contacts' | 'intelligence' | 'enrichment' | 'cadence';

function App() {
  const [currentView, setCurrentView] = useState<View>('today');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [apiHealth, setApiHealth] = useState<'healthy' | 'unhealthy' | 'checking'>('checking');

  useEffect(() => {
    checkApiHealth();
    
    // Check if first visit
    const hasSeenOnboarding = localStorage.getItem('apex_onboarding_seen');
    if (!hasSeenOnboarding) {
      setShowOnboarding(true);
    }
  }, []);

  const checkApiHealth = async () => {
    try {
      await apiClient.getHealth();
      setApiHealth('healthy');
    } catch (error) {
      console.error('API health check failed:', error);
      setApiHealth('unhealthy');
    }
  };

  const handleOnboardingClose = () => {
    setShowOnboarding(false);
    localStorage.setItem('apex_onboarding_seen', 'true');
  };

  const navItems = [
    { id: 'today' as View, label: "Today's Board", icon: Home },
    { id: 'contacts' as View, label: 'All Contacts', icon: Users },
    { id: 'intelligence' as View, label: 'Apex Intelligence', icon: Brain },
    { id: 'enrichment' as View, label: 'Enrichment', icon: Sparkles },
    { id: 'cadence' as View, label: 'Cadence', icon: Calendar },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside
        className={`bg-gradient-to-b from-gray-900 to-gray-800 text-white transition-all duration-300 ${
          sidebarOpen ? 'w-64' : 'w-20'
        } flex-shrink-0 flex flex-col`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
              <Brain className="h-6 w-6 text-white" />
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="text-xl font-bold">Apex</h1>
                <p className="text-xs text-gray-400">Intelligence</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setCurrentView(id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                currentView === id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
              title={!sidebarOpen ? label : undefined}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {sidebarOpen && <span className="font-medium">{label}</span>}
            </button>
          ))}
        </nav>

        {/* API Status */}
        <div className="p-4 border-t border-gray-700">
          <div className="flex items-center gap-2">
            <div
              className={`h-3 w-3 rounded-full ${
                apiHealth === 'healthy'
                  ? 'bg-green-500'
                  : apiHealth === 'unhealthy'
                  ? 'bg-red-500'
                  : 'bg-yellow-500 animate-pulse'
              }`}
            />
            {sidebarOpen && (
              <span className="text-sm text-gray-400">
                API {apiHealth === 'healthy' ? 'Connected' : apiHealth === 'unhealthy' ? 'Offline' : 'Checking...'}
              </span>
            )}
          </div>
        </div>

        {/* Toggle Button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-4 border-t border-gray-700 hover:bg-gray-700 transition"
        >
          {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto p-6">
          {currentView === 'today' && <TodaysBoard />}
          {currentView === 'contacts' && <ContactsBoard />}
          {currentView === 'intelligence' && <ApexIntelligence />}
          {currentView === 'enrichment' && <ContactEnrichmentView />}
          {currentView === 'cadence' && <CadenceDashboard />}
        </div>
      </main>

      {/* Onboarding Modal */}
      <OnboardingModal
        isOpen={showOnboarding}
        onClose={handleOnboardingClose}
      />
    </div>
  );
}

export default App;
