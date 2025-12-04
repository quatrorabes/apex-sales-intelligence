import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Moon, Sun, LayoutDashboard, Users, TrendingUp } from 'lucide-react';
import { ThemeProvider, useTheme } from './theme/ThemeProvider';
import TodaysBoard from './components/TodaysBoard';
import { ContactsBoard } from './components/ContactsBoard';

function AppContent() {
  const { mode, toggleTheme } = useTheme();

  return (
    <Router>
      <div className={mode === 'dark' ? 'bg-[#050816] min-h-screen' : 'bg-[#F4F5FB] min-h-screen'}>
        {/* Nav */}
        <nav className="bg-[#0B1120]/95 backdrop-blur-xl border-b border-[#94A3B8]/35 sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-6 py-3.5">
            <div className="flex items-center justify-between">
              {/* Logo */}
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#22D3EE] to-[#6366F1] flex items-center justify-center">
                  <TrendingUp className="text-white" size={20} />
                </div>
                <h1 className="text-lg font-semibold bg-gradient-to-r from-[#22D3EE] to-[#6366F1] bg-clip-text text-transparent">
                  APEX
                </h1>
              </div>

              {/* Nav Links */}
              <div className="flex items-center gap-4">
                <NavLink
                  to="/board"
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-[#22D3EE] text-[#050816]'
                        : 'text-[#CBD5E1] hover:text-[#22D3EE]'
                    }`
                  }
                >
                  <LayoutDashboard size={16} />
                  <span>Board</span>
                </NavLink>

                <NavLink
                  to="/contacts"
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-[#22D3EE] text-[#050816]'
                        : 'text-[#CBD5E1] hover:text-[#22D3EE]'
                    }`
                  }
                >
                  <Users size={16} />
                  <span>Contacts</span>
                </NavLink>
              </div>

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg border border-[#94A3B8]/35 text-[#CBD5E1] hover:bg-[#22D3EE]/10 hover:text-[#22D3EE] transition-all"
              >
                {mode === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            </div>
          </div>
        </nav>

        {/* Routes */}
        <main>
          <Routes>
            <Route path="/" element={<TodaysBoard />} />
            <Route path="/board" element={<TodaysBoard />} />
            <Route path="/contacts" element={<ContactsBoard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
