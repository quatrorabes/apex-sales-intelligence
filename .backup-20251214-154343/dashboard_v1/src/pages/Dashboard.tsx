import { AppShell } from '../layouts/AppShell';

export default function Dashboard() {
  return (
    <AppShell>
      {/* Top metric cards: span 3 columns each (4 cards = 12) */}
      <section className="col-span-12 grid grid-cols-12 gap-4">
        <div className="col-span-3 bg-slatepanel-900 shadow-card-soft shadow-card-border rounded-card px-4 py-3 flex flex-col gap-1">
          <div className="text-xs text-steel-400 uppercase tracking-wide">
            Intent Exposure
          </div>
          <div className="text-2xl font-mono">$405.091</div>
          <div className="text-[11px] text-amber-500">+12.3% vs last week</div>
        </div>

        <div className="col-span-3 bg-slatepanel-900 shadow-card-soft shadow-card-border rounded-card px-4 py-3 flex flex-col gap-1">
          <div className="text-xs text-steel-400 uppercase tracking-wide">
            Active Contacts
          </div>
          <div className="text-2xl font-mono">1,203</div>
          <div className="text-[11px] text-steel-400">Enriched in last 30 days</div>
        </div>

        <div className="col-span-3 bg-slatepanel-900 shadow-card-soft shadow-card-border rounded-card px-4 py-3 flex flex-col gap-1">
          <div className="text-xs text-steel-400 uppercase tracking-wide">
            Outreach Queue
          </div>
          <div className="text-2xl font-mono">64</div>
          <div className="text-[11px] text-steel-400">Ready for sequencing</div>
        </div>

        <div className="col-span-3 bg-slatepanel-900 shadow-card-soft shadow-card-border rounded-card px-4 py-3 flex flex-col gap-1">
          <div className="text-xs text-steel-400 uppercase tracking-wide">
            Intelligence Coverage
          </div>
          <div className="text-2xl font-mono">72%</div>
          <div className="h-1.5 mt-1 rounded-full bg-slatepanel-800 overflow-hidden">
            <div className="h-full w-[72%] bg-teal-500" />
          </div>
        </div>
      </section>

      {/* Middle row: left = table (span 8); right = chart (span 4) */}
      <section className="col-span-8 bg-slatepanel-900 shadow-card-soft shadow-card-border rounded-card p-4 mt-2">
        <header className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-steel-100">
            Priority Contacts
          </h2>
          <span className="text-[11px] text-steel-400 font-mono">
            Sorted by MDCP score
          </span>
        </header>

        <div className="border border-slatepanel-700 rounded-[4px] overflow-hidden">
          <table className="w-full text-xs">
            <thead className="bg-slatepanel-800 text-steel-400">
              <tr>
                <th className="px-3 py-2 text-left font-medium">Name</th>
                <th className="px-3 py-2 text-left font-medium">Company</th>
                <th className="px-3 py-2 text-left font-medium">Role</th>
                <th className="px-3 py-2 text-right font-medium">MDCP</th>
                <th className="px-3 py-2 text-right font-medium">Urgency</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: 'Mark Root', company: 'HFF', role: 'Managing Director', score: 92, urgency: 'High' },
                { name: 'Jason Oberman', company: 'Blox Ventures', role: 'CEO', score: 88, urgency: 'High' },
                { name: 'Greg Dill', company: 'US Bank', role: 'SBA Partner', score: 81, urgency: 'Medium' },
              ].map((row, idx) => (
                <tr
                  key={row.name}
                  className={idx % 2 === 0 ? 'bg-slatepanel-900' : 'bg-slatepanel-800/40 hover:bg-slatepanel-800'}
                >
                  <td className="px-3 py-2 text-sm">{row.name}</td>
                  <td className="px-3 py-2 text-xs text-steel-400">{row.company}</td>
                  <td className="px-3 py-2 text-xs text-steel-400">{row.role}</td>
                  <td className="px-3 py-2 text-right font-mono text-sm">{row.score}</td>
                  <td className="px-3 py-2 text-right text-xs">
                    <span
                      className={[
                        'inline-flex items-center px-2 py-0.5 rounded-full border text-[11px]',
                        row.urgency === 'High'
                          ? 'border-teal-500 text-teal-500'
                          : 'border-steel-400 text-steel-400',
                      ].join(' ')}
                    >
                      {row.urgency}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="col-span-4 bg-slatepanel-900 shadow-card-soft shadow-card-border rounded-card p-4 mt-2 flex flex-col">
        <header className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-steel-100">
            Pipeline Momentum
          </h2>
          <span className="text-[11px] text-steel-400">Last 30 days</span>
        </header>
        <div className="flex-1 flex flex-col justify-center">
          {/* Placeholder chart blocks: can be wired to real charts later */}
          <div className="h-32 flex items-end gap-1">
            {[40, 55, 70, 65, 80, 72, 90].map((h, idx) => (
              <div
                key={idx}
                style={{ height: `${h}%` }}
                className="flex-1 bg-teal-500/70 rounded-[2px]"
              />
            ))}
          </div>
          <div className="mt-3 text-[11px] text-steel-400 font-mono">
            Deals touched vs. enriched contacts
          </div>
        </div>
      </section>
    </AppShell>
  );
}
