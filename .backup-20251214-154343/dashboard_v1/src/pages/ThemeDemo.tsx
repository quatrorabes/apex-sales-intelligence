/**
 * APEX THEME DEMO PAGE
 * Warm Midnight Design System Showcase
 */
import React from 'react';
import { ProspectCard } from '../components/ProspectCard';
import { KPICard } from '../components/KPICard';
import { buttonClasses } from '../styles/componentClasses';

export const ThemeDemo: React.FC = () => {
  return (
    <div className="min-h-screen bg-midnight-950 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-12">
        <h1 className="text-5xl font-bold text-text-primary mb-3">
          Warm Midnight Theme
        </h1>
        <p className="text-text-secondary text-lg">
          APEX Sales Intelligence Design System v1.0
        </p>
      </div>

      <div className="max-w-7xl mx-auto space-y-12">
        {/* KPI Cards Section */}
        <section>
          <h2 className="text-2xl font-semibold text-text-primary mb-6">
            KPI Cards
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <KPICard
              label="Hot Prospects"
              value="127"
              trend={{ value: 23, isPositive: true }}
              delay={0}
            />
            <KPICard
              label="Pipeline Value"
              value="$2.4M"
              trend={{ value: 12, isPositive: true }}
              delay={0.1}
            />
            <KPICard
              label="Avg Response Time"
              value="4.2h"
              trend={{ value: 8, isPositive: false }}
              delay={0.2}
            />
          </div>
        </section>

        {/* Prospect Cards Section */}
        <section>
          <h2 className="text-2xl font-semibold text-text-primary mb-6">
            Prospect Cards
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Hot Prospect with AI */}
            <ProspectCard
              name="Sarah Chen"
              company="TechVentures Inc."
              score={92}
              aiReason="Recently promoted to VP of Engineering. Company just raised Series B ($45M). Posted about scaling challenges on LinkedIn 2 days ago."
              tags={['Decision Maker', 'Enterprise', 'High Intent']}
            />

            {/* Warm Prospect */}
            <ProspectCard
              name="Michael Rodriguez"
              company="DataFlow Systems"
              score={76}
              tags={['Mid-Market', 'Engaged', 'Follow-up']}
            />

            {/* Hot Prospect - No AI */}
            <ProspectCard
              name="Emily Watson"
              company="CloudScale Analytics"
              score={88}
              tags={['Champion', 'Budget Confirmed']}
            />

            {/* Cold Prospect with AI */}
            <ProspectCard
              name="James Park"
              company="Legacy Systems Corp"
              score={45}
              aiReason="Company recently underwent restructuring. IT budget frozen for Q4. Recommend nurturing campaign until Q1 2026."
              tags={['Nurture', 'Budget Constraints']}
            />
          </div>
        </section>

        {/* Buttons Section */}
        <section>
          <h2 className="text-2xl font-semibold text-text-primary mb-6">
            Button Variants
          </h2>
          <div className="flex flex-wrap gap-4">
            <button className={buttonClasses.primary}>
              Primary Action
            </button>
            <button className={buttonClasses.secondary}>
              Secondary Action
            </button>
            <button className={buttonClasses.action}>
              Quick Action
            </button>
          </div>
        </section>

        {/* AI Insight Bubbles */}
        <section>
          <h2 className="text-2xl font-semibold text-text-primary mb-6">
            AI Insight Bubbles
          </h2>
          <div className="space-y-4 max-w-2xl">
            {/* Gold Response */}
            <div className="flex justify-end">
              <div className="bg-gradient-to-r from-gold to-gold-hover text-midnight-950 px-6 py-4 rounded-2xl rounded-tr-sm max-w-lg shadow-gold-glow">
                <p className="font-semibold mb-1">APEX Intelligence</p>
                <p>Sarah Chen is currently in active buying mode. Her company just secured Series B funding and she's been researching solutions like yours. Recommend reaching out within 48 hours.</p>
              </div>
            </div>

            {/* Blue AI Insight */}
            <div className="flex justify-start">
              <div className="bg-blue-muted border-l-4 border-blue px-6 py-4 rounded-2xl rounded-tl-sm max-w-lg shadow-blue-glow">
                <p className="text-blue font-semibold mb-1 flex items-center gap-2">
                  <span>✨</span> AI Analysis
                </p>
                <p className="text-text-secondary italic">
                  Based on recent activity, this prospect shows 3x higher engagement than average. Their LinkedIn posts suggest urgent need for infrastructure scaling.
                </p>
              </div>
            </div>

            {/* Status Update */}
            <div className="flex justify-end">
              <div className="bg-midnight-800 border border-midnight-600 text-text-primary px-6 py-4 rounded-2xl rounded-tr-sm max-w-lg">
                <p className="text-text-tertiary text-sm mb-1">System Update</p>
                <p>Enrichment complete. 127 new data points added. Score updated from 76 → 92.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Score Legend */}
        <section>
          <h2 className="text-2xl font-semibold text-text-primary mb-6">
            Scoring System
          </h2>
          <div className="bg-midnight-900 border border-midnight-600 rounded-card p-6">
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="text-gold text-4xl font-bold w-16">85+</div>
                <div>
                  <p className="text-text-primary font-semibold">Hot Prospect</p>
                  <p className="text-text-secondary text-sm">High buying intent, immediate action recommended</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-coral text-4xl font-semibold w-16">60-84</div>
                <div>
                  <p className="text-text-primary font-semibold">Warm Prospect</p>
                  <p className="text-text-secondary text-sm">Engaged and qualified, nurture relationship</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-text-tertiary text-4xl font-medium w-16">&lt;60</div>
                <div>
                  <p className="text-text-primary font-semibold">Cold Prospect</p>
                  <p className="text-text-secondary text-sm">Low priority, long-term nurture campaign</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Color Palette */}
        <section className="pb-12">
          <h2 className="text-2xl font-semibold text-text-primary mb-6">
            Color Palette
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <div className="bg-gold h-20 rounded-lg shadow-gold-glow"></div>
              <p className="text-text-secondary text-sm font-mono">#E5B84C</p>
              <p className="text-text-tertiary text-xs">Primary Gold</p>
            </div>
            <div className="space-y-2">
              <div className="bg-blue h-20 rounded-lg shadow-blue-glow"></div>
              <p className="text-text-secondary text-sm font-mono">#3B82F6</p>
              <p className="text-text-tertiary text-xs">AI Deep Blue</p>
            </div>
            <div className="space-y-2">
              <div className="bg-coral h-20 rounded-lg"></div>
              <p className="text-text-secondary text-sm font-mono">#F97316</p>
              <p className="text-text-tertiary text-xs">Warm Coral</p>
            </div>
            <div className="space-y-2">
              <div className="bg-lime h-20 rounded-lg"></div>
              <p className="text-text-secondary text-sm font-mono">#BFFF00</p>
              <p className="text-text-tertiary text-xs">Success Lime</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};