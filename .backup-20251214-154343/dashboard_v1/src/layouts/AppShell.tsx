import { ReactNode } from 'react';
import { useLocation, Link } from 'react-router-dom';

interface AppShellProps {
  children: ReactNode;
}

const navItems = [
  { key: 'dashboard', label: 'Dashboard', icon: '◎', to: '/' },
  { key: 'board', label: "Today's Board", icon: '▤', to: '/todays-board' },
  { key: 'contacts', label: 'Contacts', icon: '◉', to: '/contacts' },
];

export function AppShell({ children }: AppShellProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen w-full bg-void-900 text-slate-100">
      {/* Subtle gradient overlay */}
      <div className="fixed inset-0 bg-gradient-to-br from-azure-600/5 via-transparent to-transparent pointer-events-none" />
      
      <div className="relative flex flex-col min-h-screen">
        {/* Top Header - Glass */}
        <header className="h-16 px-6 flex items-center justify-between bg-void-850/80 backdrop-blur-xl border-b border-glass-border">
          <div className="flex items-center gap-4">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-azure-500 to-azure-600 flex items-center justify-center text-sm font-bold shadow-glow-blue">
              AX
            </div>
            <div className="flex flex-col">
              <span className="text-base font-semibold text-slate-50">
                Apex Sales Intelligence
              </span>
              <span className="text-xs text-slate-500">
                Enterprise Dashboard
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-glass-white border border-glass-border flex items-center justify-center text-xs text-slate-400">
              CR
            </div>
          </div>
        </header>

        {/* Body */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar - Glass */}
          <aside className="w-60 bg-void-850/60 backdrop-blur-xl border-r border-glass-border flex flex-col">
            <div className="px-4 py-5">
              <div className="text-[10px] font-medium text-slate-500 uppercase tracking-widest mb-4">
                Navigation
              </div>
              <nav className="space-y-1">
                {navItems.map((item) => {
                  const active = location.pathname === item.to || 
                    (item.to !== '/' && location.pathname.startsWith(item.to));
                  return (
                    <Link
                      key={item.key}
                      to={item.to}
                      className={`group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all duration-200 ${
                        active
                          ? 'bg-azure-600/20 text-azure-300 border border-azure-600/30'
                          : 'text-slate-400 hover:bg-glass-hover hover:text-slate-200 border border-transparent'
                      }`}
                    >
                      <span className={`text-base ${active ? 'text-azure-400' : 'text-slate-500 group-hover:text-slate-300'}`}>
                        {item.icon}
                      </span>
                      <span className="font-medium">{item.label}</span>
                      {active && (
                        <span className="ml-auto w-1.5 h-1.5 rounded-full bg-azure-400 shadow-glow-blue" />
                      )}
                    </Link>
                  );
                })}
              </nav>
            </div>
            
            {/* Sidebar Footer */}
            <div className="mt-auto px-4 py-4 border-t border-glass-border">
              <div className="px-3 py-3 rounded-xl bg-glass-white border border-glass-border">
                <div className="text-xs text-slate-400 mb-1">Intelligence Status</div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-sm text-slate-300">1,226 contacts</span>
                </div>
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 overflow-auto">
            <div className="max-w-7xl mx-auto px-8 py-8">
              <div className="grid grid-cols-12 gap-6">
                {children}
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
