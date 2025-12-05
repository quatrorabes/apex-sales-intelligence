// =============================================================================
// FILE: /dashboard_v1/src/components/ContactDetailPage.tsx
// APEX SALES INTELLIGENCE - WORLD-CLASS CONTACT DETAIL
// Version: 2.0 GOLD | December 4, 2025
// =============================================================================

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

// =============================================================================
// DESIGN TOKENS - WARM MIDNIGHT
// =============================================================================
const colors = {
  midnight: {
    950: '#0A0A0A',
    900: '#141414',
    800: '#1C1C1C',
    700: '#262626',
    600: '#2A2A2A',
    500: '#3D3D3D',
  },
  gold: {
    DEFAULT: '#E5B84C',
    hover: '#D4A853',
    muted: 'rgba(229, 184, 76, 0.15)',
    glow: 'rgba(229, 184, 76, 0.25)',
  },
  violet: {
    DEFAULT: '#A78BFA',
    muted: 'rgba(167, 139, 250, 0.15)',
  },
  lime: '#BFFF00',
  coral: '#F97316',
  red: '#EF4444',
  text: {
    primary: '#FAFAFA',
    secondary: '#A3A3A3',
    tertiary: '#737373',
  },
};

// =============================================================================
// TYPES
// =============================================================================
interface Contact {
  id: number;
  name: string;
  firstname?: string;
  lastname?: string;
  title: string;
  company: string;
  email: string;
  phone?: string;
  linkedin_url?: string;
  mdcp_score?: number;
  mdcp_tier?: string;
  enriched?: boolean;
  enriched_at?: string;
  profile_content?: string;
  enrichment_status?: string;
}

interface MBTIData {
  type: string;
  confidence: string;
  evidence: string;
  traits: { name: string; description: string }[];
  workStyle: string;
  bestApproach: string;
}

interface DISCData {
  primary: string;
  secondary: string;
  percentages: { D: number; I: number; S: number; C: number };
  indicators: string;
  doList: string[];
  dontList: string[];
  decisionStyle: string;
  motivators: string[];
  stressors: string[];
}

interface PainPoint {
  number: number;
  title: string;
  description: string;
}

interface CompanyData {
  name: string;
  serviceModel: string;
  valueProposition: string;
  coreOfferings: string[];
  targetMarkets: string[];
  industry: string;
  competitors: string[];
  advantages: string[];
  leadership: string;
  culture: string[];
  headquarters?: string;
}

interface TriggerEvent {
  title: string;
  description: string;
}

// =============================================================================
// INLINE SVG ICONS
// =============================================================================
const Icons = {
  ArrowLeft: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>,
  Mail: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>,
  Phone: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>,
  Linkedin: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/>ircle cx="4" cy="4" r="2"/></svg>,
  RefreshCw: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 2v6h-6M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6M21 12a9 9 0 0 1-15 6.7L3 16"/></svg>,
  Check: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>,
  Sparkles: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>,
  Building: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/></svg>,
  Target: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">ircle cx="12" cy="12" r="10"/>ircle cx="12" cy="12" r="6"/>ircle cx="12" cy="12" r="2"/></svg>,
  TrendingUp: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>,
  Brain: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-1.54M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-1.54"/></svg>,
  MessageSquare: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  Zap: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
};

// =============================================================================
// ANIMATION VARIANTS
// =============================================================================
const cardVariants = {
  initial: { opacity: 0, y: 20, scale: 0.98 },
  animate: { opacity: 1, y: 0, scale: 1 },
};

const tabContentVariants = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
};

const staggerContainer = {
  animate: { transition: { staggerChildren: 0.05 } },
};

// =============================================================================
// PARSING UTILITIES
// =============================================================================
const parseExecutiveSummary = (content: string): string => {
  const match = content.match(/## EXECUTIVE SUMMARY\n\n([\s\S]*?)(?=\n---)/);
  return match?.[1]?.trim() || '';
};

const parseOverview = (content: string): { role: string; responsibilities: string[]; reporting: string } => {
  const overviewSection = content.match(/### Overview\n\n([\s\S]*?)(?=### Background)/)?.[1] || '';
  
  const roleMatch = overviewSection.match(/\*\*Current Role & Organization\*\*\n\n([\s\S]*?)(?=\*\*Key Responsibilities)/);
  const respMatch = overviewSection.match(/\*\*Key Responsibilities & Areas of Focus\*\*\n\n([\s\S]*?)(?=\*\*Reporting Structure)/);
  const reportMatch = overviewSection.match(/\*\*Reporting Structure & Team Dynamics\*\*\n\n([\s\S]*?)$/);

  const responsibilities = respMatch?.[1]
    ?.split('\n')
    .filter(line => line.startsWith('- '))
    .map(line => line.replace(/^- /, '').trim()) || [];

  return {
    role: roleMatch?.[1]?.trim() || '',
    responsibilities,
    reporting: reportMatch?.[1]?.trim() || '',
  };
};

const parseBackground = (content: string): { trajectory: string; competencies: string[]; positioning: string } => {
  const bgSection = content.match(/### Background & Experience\n\n([\s\S]*?)(?=### Education)/)?.[1] || '';
  
  const trajectoryMatch = bgSection.match(/\*\*Career Trajectory\*\*\n\n([\s\S]*?)(?=\*\*Core Competencies)/);
  const compMatch = bgSection.match(/\*\*Core Competencies & Specializations\*\*\n\n([\s\S]*?)(?=\*\*Professional Positioning)/);
  const posMatch = bgSection.match(/\*\*Professional Positioning\*\*\n\n([\s\S]*?)$/);

  const competencies = compMatch?.[1]
    ?.split('\n')
    .filter(line => line.startsWith('- '))
    .map(line => line.replace(/^- /, '').trim()) || [];

  return {
    trajectory: trajectoryMatch?.[1]?.trim() || '',
    competencies,
    positioning: posMatch?.[1]?.trim() || '',
  };
};

const parseMBTI = (content: string): MBTIData | null => {
  const mbtiSection = content.match(/\*\*Myers-Briggs Type Indicator \(MBTI\)\*\*\n\n([\s\S]*?)(?=\*\*DISC Profile Assessment\*\*)/)?.[1];
  if (!mbtiSection) return null;

  const typeMatch = mbtiSection.match(/\*\*Inferred Type\*\*:\s*(\w{4})/);
  const confidenceMatch = mbtiSection.match(/\*\*Confidence Level\*\*:\s*([^\n]+)/);
  const evidenceMatch = mbtiSection.match(/\*\*Evidence\*\*:\s*([^\n]+(?:\n(?!\*\*)[^\n]+)*)/);
  const workStyleMatch = mbtiSection.match(/\*\*Work Style Implications\*\*:\s*([^\n]+(?:\n(?!\*\*)[^\n]+)*)/);
  const approachMatch = mbtiSection.match(/\*\*Best Communication Approach\*\*:\s*([^\n]+(?:\n(?!\*\*)[^\n]+)*)/);

  // Parse traits
  const traitsSection = mbtiSection.match(/\*\*Key Traits\*\*:\n([\s\S]*?)(?=\*\*Work Style)/)?.[1] || '';
  const traits = [...traitsSection.matchAll(/\*\*([^*]+)\*\*:\s*([^\n]+)/g)].map(m => ({
    name: m[1].trim(),
    description: m[2].trim(),
  }));

  return {
    type: typeMatch?.[1] || 'Unknown',
    confidence: confidenceMatch?.[1]?.trim() || 'Medium',
    evidence: evidenceMatch?.[1]?.trim() || '',
    traits,
    workStyle: workStyleMatch?.[1]?.trim() || '',
    bestApproach: approachMatch?.[1]?.trim() || '',
  };
};

const parseDISC = (content: string): DISCData | null => {
  const discSection = content.match(/\*\*DISC Profile Assessment\*\*\n\n([\s\S]*?)(?=### Social Presence|---)/)?.[1];
  if (!discSection) return null;

  const primaryMatch = discSection.match(/\*\*Primary Style\*\*:\s*([DISC])/);
  const secondaryMatch = discSection.match(/\*\*Secondary Style\*\*:\s*([DISC])/);
  const percentMatch = discSection.match(/\*\*Percentage Estimate\*\*:\s*D:\s*(\d+)%,\s*I:\s*(\d+)%,\s*S:\s*(\d+)%,\s*C:\s*(\d+)%/);
  const indicatorsMatch = discSection.match(/\*\*Behavioral Indicators\*\*:\s*([^\n]+(?:\n(?!\*\*)[^\n]+)*)/);
  const decisionMatch = discSection.match(/\*\*Decision-Making Style\*\*:\s*([^\n]+(?:\n(?!\*\*)[^\n]+)*)/);

  // Parse Do/Don't lists
  const doMatch = discSection.match(/\*\*Do\*\*:\s*([^\n]+)/);
  const dontMatch = discSection.match(/\*\*Don't\*\*:\s*([^\n]+)/);

  // Parse motivators and stressors
  const motivatorsMatch = discSection.match(/\*\*Motivators\*\*:\s*([^\n]+)/);
  const stressorsMatch = discSection.match(/\*\*Stressors\*\*:\s*([^\n]+)/);

  return {
    primary: primaryMatch?.[1] || '?',
    secondary: secondaryMatch?.[1] || '?',
    percentages: {
      D: parseInt(percentMatch?.[1] || '0'),
      I: parseInt(percentMatch?.[2] || '0'),
      S: parseInt(percentMatch?.[3] || '0'),
      C: parseInt(percentMatch?.[4] || '0'),
    },
    indicators: indicatorsMatch?.[1]?.trim() || '',
    doList: doMatch?.[1]?.split(/[.;]/).filter(s => s.trim()).map(s => s.trim()) || [],
    dontList: dontMatch?.[1]?.split(/[.;]/).filter(s => s.trim()).map(s => s.trim()) || [],
    decisionStyle: decisionMatch?.[1]?.trim() || '',
    motivators: motivatorsMatch?.[1]?.split(',').map(s => s.trim()) || [],
    stressors: stressorsMatch?.[1]?.split(',').map(s => s.trim()) || [],
  };
};

const parseCompany = (content: string): CompanyData | null => {
  const companyMatch = content.match(/## ([^-\n]+) - COMPANY INTELLIGENCE\n\n([\s\S]*?)(?=## SALES OPPORTUNITY|$)/);
  if (!companyMatch) return null;

  const companyName = companyMatch[1].trim();
  const companySection = companyMatch[2];

  const serviceModelMatch = companySection.match(/\*\*Service Delivery Model\*\*\n\n([^\n]+(?:\n(?!\*\*)[^\n]+)*)/);
  const valueMatch = companySection.match(/\*\*Value Proposition\*\*\n\n([^\n]+(?:\n(?!\*\*|\n###)[^\n]+)*)/);
  const industryMatch = companySection.match(/\*\*Industry Category\*\*\n\n([^\n]+)/);
  const leadershipMatch = companySection.match(/\*\*Leadership Profile\*\*\n\n([^\n]+(?:\n(?!\*\*)[^\n]+)*)/);

  // Parse bullet lists
  const offeringsSection = companySection.match(/\*\*Core Offerings\*\*\n\n([\s\S]*?)(?=\*\*Target Markets|###)/)?.[1] || '';
  const offerings = offeringsSection.split('\n').filter(l => l.startsWith('- ')).map(l => l.replace(/^- /, '').trim());

  const marketsSection = companySection.match(/\*\*Target Markets & Customer Segments\*\*\n\n([\s\S]*?)(?=\*\*Pricing|###)/)?.[1] || '';
  const markets = marketsSection.split('\n').filter(l => l.startsWith('- ')).map(l => l.replace(/^- /, '').trim());

  const advantagesSection = companySection.match(/\*\*Competitive Advantages & Differentiation\*\*\n\n([\s\S]*?)(?=\*\*Market Share|###)/)?.[1] || '';
  const advantages = advantagesSection.split('\n').filter(l => l.startsWith('- ')).map(l => l.replace(/^- /, '').trim());

  const cultureSection = companySection.match(/\*\*Company Culture & Values\*\*\n\n([\s\S]*?)(?=###|---)/)?.[1] || '';
  const culture = cultureSection.split('\n').filter(l => l.startsWith('- ')).map(l => l.replace(/^- /, '').trim());

  return {
    name: companyName,
    serviceModel: serviceModelMatch?.[1]?.trim() || '',
    valueProposition: valueMatch?.[1]?.trim() || '',
    coreOfferings: offerings,
    targetMarkets: markets,
    industry: industryMatch?.[1]?.trim() || '',
    competitors: [],
    advantages,
    leadership: leadershipMatch?.[1]?.trim() || '',
    culture,
  };
};

const parsePainPoints = (content: string): PainPoint[] => {
  const painSection = content.match(/\*\*Role-Specific Pain Points[^*]*\*\*\n\n([\s\S]*?)(?=\*\*Industry-Specific|---)/)?.[1] || '';
  
  const painPoints: PainPoint[] = [];
  const matches = [...painSection.matchAll(/\*\*Pain Point (\d+) - ([^*]+)\*\*:\s*([^*]+?)(?=\n\n\*\*Pain Point|\n\n\*\*Industry|$)/gs)];
  
  matches.forEach(match => {
    painPoints.push({
      number: parseInt(match[1]),
      title: match[2].trim(),
      description: match[3].trim(),
    });
  });

  return painPoints;
};

const parseTriggerEvents = (content: string): TriggerEvent[] => {
  const triggerSection = content.match(/\*\*Current Conditions Creating Opportunity\*\*\n\n([\s\S]*?)(?=\*\*Regulatory|###)/)?.[1] || '';
  
  const events: TriggerEvent[] = [];
  const matches = [...triggerSection.matchAll(/- \*\*([^*]+)\*\*:\s*([^\n]+(?:\n(?!- \*\*)[^\n]+)*)/g)];
  
  matches.forEach(match => {
    events.push({
      title: match[1].trim(),
      description: match[2].trim(),
    });
  });

  return events;
};

// =============================================================================
// UTILITY COMPONENTS
// =============================================================================
const ScoreBadge: React.FC<{ score: number; size?: 'sm' | 'lg' }> = ({ score, size = 'lg' }) => {
  const getScoreStyle = () => {
    if (score >= 85) return { bg: colors.gold.muted, text: colors.gold.DEFAULT, glow: `0 0 30px ${colors.gold.glow}` };
    if (score >= 60) return { bg: 'rgba(249, 115, 22, 0.15)', text: colors.coral, glow: '0 0 20px rgba(249, 115, 22, 0.2)' };
    return { bg: 'rgba(115, 115, 115, 0.15)', text: colors.text.tertiary, glow: 'none' };
  };

  const style = getScoreStyle();
  const sizeClasses = size === 'lg' ? 'w-20 h-20 text-3xl' : 'w-12 h-12 text-lg';

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      className={`${sizeClasses} rounded-2xl flex flex-col items-center justify-center font-bold`}
      style={{ backgroundColor: style.bg, color: style.text, boxShadow: style.glow }}
    >
      <span>{score}</span>
      {size === 'lg' && <span className="text-xs font-medium opacity-70">MDCP</span>}
    </motion.div>
  );
};

const Card: React.FC<{ children: React.ReactNode; className?: string; elevated?: boolean; glow?: boolean }> = ({ 
  children, className = '', elevated = false, glow = false 
}) => (
  <motion.div
    variants={cardVariants}
    initial="initial"
    animate="animate"
    transition={{ duration: 0.3 }}
    className={`rounded-2xl p-6 ${className}`}
    style={{
      backgroundColor: elevated ? colors.midnight[800] : colors.midnight[900],
      border: `1px solid ${glow ? 'rgba(229, 184, 76, 0.3)' : colors.midnight[600]}`,
      boxShadow: glow ? '0 0 30px rgba(229, 184, 76, 0.1)' : 'none',
    }}
  >
    {children}
  </motion.div>
);

const SectionTitle: React.FC<{ emoji?: string; children: React.ReactNode }> = ({ emoji, children }) => (
  <h3 className="text-lg font-semibold flex items-center gap-2 mb-4" style={{ color: colors.text.primary }}>
    {emoji && <span>{emoji}</span>}
    {children}
  </h3>
);

const Label: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <span className="text-xs font-medium uppercase tracking-wider" style={{ color: colors.text.tertiary }}>
    {children}
  </span>
);

const EmptyState: React.FC<{ message: string }> = ({ message }) => (
  <Card>
    <div className="text-center py-12">
      <div className="text-4xl mb-3">📭</div>
      <p style={{ color: colors.text.tertiary }}>{message}</p>
    </div>
  </Card>
);

// =============================================================================
// TAB CONFIGURATION
// =============================================================================
const tabs = [
  { id: 'overview', label: 'Overview', emoji: '📊', icon: Icons.TrendingUp },
  { id: 'professional', label: 'Professional', emoji: '🧠', icon: Icons.Brain },
  { id: 'company', label: 'Company', emoji: '🏢', icon: Icons.Building },
  { id: 'pain-points', label: 'Pain Points', emoji: '🎯', icon: Icons.Target },
  { id: 'sales-intel', label: 'Sales Intel', emoji: '💰', icon: Icons.Zap },
  { id: 'outreach', label: 'Outreach', emoji: '✉️', icon: Icons.MessageSquare },
];

// =============================================================================
// TAB NAVIGATION
// =============================================================================
const TabNav: React.FC<{ activeTab: string; onTabChange: (tab: string) => void; hasContent: Record<string, boolean> }> = ({ 
  activeTab, onTabChange, hasContent 
}) => (
  <div className="flex gap-1 p-1.5 rounded-xl overflow-x-auto" style={{ backgroundColor: colors.midnight[900] }}>
    {tabs.map((tab) => {
      const isActive = activeTab === tab.id;
      const hasData = hasContent[tab.id];
      return (
        <motion.button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="relative flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all whitespace-nowrap"
          style={{
            backgroundColor: isActive ? colors.midnight[700] : 'transparent',
            color: isActive ? colors.text.primary : colors.text.secondary,
          }}
        >
          <span>{tab.emoji}</span>
          {tab.label}
          {hasData && !isActive && (
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: colors.gold.DEFAULT }} />
          )}
        </motion.button>
      );
    })}
  </div>
);

// =============================================================================
// DISC PROGRESS BAR
// =============================================================================
const DISCBar: React.FC<{ style: string; name: string; score: number; indicators: string; index: number }> = ({ 
  style, name, score, indicators, index 
}) => {
  const discColors: Record<string, string> = {
    D: colors.red,
    I: colors.gold.DEFAULT,
    S: colors.lime,
    C: colors.violet.DEFAULT,
  };
  const color = discColors[style] || colors.text.tertiary;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="mb-5"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <span
            className="w-10 h-10 rounded-lg flex items-center justify-center text-lg font-black"
            style={{ backgroundColor: `${color}15`, color }}
          >
            {style}
          </span>
          <span className="text-sm font-medium" style={{ color: colors.text.primary }}>{name}</span>
        </div>
        <span className="text-lg font-bold tabular-nums" style={{ color }}>{score}%</span>
      </div>
      <div className="h-3 rounded-full overflow-hidden" style={{ backgroundColor: colors.midnight[700] }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.8, delay: 0.2 + index * 0.1, ease: 'easeOut' }}
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
        />
      </div>
      {indicators && (
        <p className="text-xs mt-2 pl-13" style={{ color: colors.text.tertiary, paddingLeft: '52px' }}>
          {indicators.slice(0, 100)}{indicators.length > 100 ? '...' : ''}
        </p>
      )}
    </motion.div>
  );
};

// =============================================================================
// OVERVIEW TAB
// =============================================================================
const OverviewTab: React.FC<{ content: string; contact: Contact }> = ({ content, contact }) => {
  const summary = parseExecutiveSummary(content);
  const overview = parseOverview(content);
  const background = parseBackground(content);

  return (
    <motion.div variants={staggerContainer} initial="initial" animate="animate" className="space-y-6">
      {/* Executive Summary */}
      <Card glow>
        <SectionTitle emoji="📋">Executive Summary</SectionTitle>
        <p className="text-sm leading-relaxed" style={{ color: colors.text.secondary }}>
          {summary || `No profile data available for ${contact.name}. Click "Enrich" to generate intelligence.`}
        </p>
      </Card>

      {/* Current Role */}
      {overview.role && (
        <Card>
          <SectionTitle emoji="💼">Current Role</SectionTitle>
          <p className="text-sm leading-relaxed mb-4" style={{ color: colors.text.secondary }}>{overview.role}</p>
          
          {overview.responsibilities.length > 0 && (
            <>
              <Label>Key Responsibilities</Label>
              <ul className="mt-2 space-y-1">
                {overview.responsibilities.slice(0, 6).map((resp, i) => (
                  <li key={i} className="text-sm flex items-start gap-2" style={{ color: colors.text.secondary }}>
                    <span style={{ color: colors.gold.DEFAULT }}>•</span>
                    {resp}
                  </li>
                ))}
              </ul>
            </>
          )}
        </Card>
      )}

      {/* Career & Competencies */}
      {(background.trajectory || background.competencies.length > 0) && (
        <Card>
          <SectionTitle emoji="📈">Background & Experience</SectionTitle>
          {background.trajectory && (
            <p className="text-sm leading-relaxed mb-4" style={{ color: colors.text.secondary }}>
              {background.trajectory}
            </p>
          )}
          
          {background.competencies.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-4">
              {background.competencies.map((comp, i) => (
                <span
                  key={i}
                  className="px-3 py-1 rounded-full text-xs font-medium"
                  style={{ backgroundColor: colors.midnight[800], color: colors.text.secondary }}
                >
                  {comp}
                </span>
              ))}
            </div>
          )}
        </Card>
      )}
    </motion.div>
  );
};

// =============================================================================
// PROFESSIONAL TAB
// =============================================================================
const ProfessionalTab: React.FC<{ content: string }> = ({ content }) => {
  const mbti = parseMBTI(content);
  const disc = parseDISC(content);

  const discNames: Record<string, string> = {
    D: 'Dominance',
    I: 'Influence',
    S: 'Steadiness',
    C: 'Conscientiousness',
  };

  return (
    <motion.div variants={staggerContainer} initial="initial" animate="animate" className="space-y-6">
      {/* MBTI Card */}
      <Card>
        <div className="flex items-center justify-between mb-6">
          <SectionTitle emoji="🧠">Myers-Briggs Assessment</SectionTitle>
          {mbti && (
            <div className="flex items-center gap-3">
              <span className="text-3xl font-black tracking-wider" style={{ color: colors.violet.DEFAULT }}>
                {mbti.type}
              </span>
              <span
                className="px-3 py-1 rounded-lg text-xs font-medium"
                style={{ backgroundColor: colors.violet.muted, color: colors.violet.DEFAULT }}
              >
                {mbti.confidence}
              </span>
            </div>
          )}
        </div>

        {mbti ? (
          <>
            {/* Evidence */}
            <div className="mb-6 p-4 rounded-xl" style={{ backgroundColor: colors.midnight[800] }}>
              <Label>Evidence</Label>
              <p className="text-sm mt-2 leading-relaxed" style={{ color: colors.text.secondary }}>
                {mbti.evidence}
              </p>
            </div>

            {/* Key Traits */}
            {mbti.traits.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {mbti.traits.map((trait, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 + i * 0.05 }}
                    className="p-4 rounded-xl"
                    style={{ backgroundColor: colors.midnight[800] }}
                  >
                    <div className="text-sm font-semibold mb-1" style={{ color: colors.violet.DEFAULT }}>
                      {trait.name}
                    </div>
                    <p className="text-xs leading-relaxed" style={{ color: colors.text.secondary }}>
                      {trait.description}
                    </p>
                  </motion.div>
                ))}
              </div>
            )}

            {/* Work Style */}
            {mbti.workStyle && (
              <div className="p-4 rounded-xl border-l-4" style={{ backgroundColor: colors.violet.muted, borderColor: colors.violet.DEFAULT }}>
                <Label>Work Style</Label>
                <p className="text-sm mt-2 leading-relaxed" style={{ color: colors.text.primary }}>
                  {mbti.workStyle}
                </p>
              </div>
            )}

            {/* Best Communication Approach */}
            {mbti.bestApproach && (
              <div className="mt-4 p-4 rounded-xl" style={{ backgroundColor: colors.gold.muted }}>
                <Label>Best Communication Approach</Label>
                <p className="text-sm mt-2 leading-relaxed" style={{ color: colors.text.primary }}>
                  {mbti.bestApproach}
                </p>
              </div>
            )}
          </>
        ) : (
          <EmptyState message="No MBTI data available. Enrich this contact to generate." />
        )}
      </Card>

      {/* DISC Card */}
      <Card>
        <div className="flex items-center justify-between mb-6">
          <SectionTitle emoji="📊">DISC Profile</SectionTitle>
          {disc && (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Label>Primary</Label>
                <span
                  className="text-xl font-black w-9 h-9 rounded-lg flex items-center justify-center"
                  style={{
                    backgroundColor: disc.primary === 'D' ? `${colors.red}15` : disc.primary === 'I' ? colors.gold.muted : disc.primary === 'S' ? 'rgba(191, 255, 0, 0.15)' : colors.violet.muted,
                    color: disc.primary === 'D' ? colors.red : disc.primary === 'I' ? colors.gold.DEFAULT : disc.primary === 'S' ? colors.lime : colors.violet.DEFAULT,
                  }}
                >
                  {disc.primary}
                </span>
              </div>
              <div className="w-px h-6" style={{ backgroundColor: colors.midnight[600] }} />
              <div className="flex items-center gap-2">
                <Label>Secondary</Label>
                <span
                  className="text-xl font-black w-9 h-9 rounded-lg flex items-center justify-center"
                  style={{
                    backgroundColor: disc.secondary === 'D' ? `${colors.red}15` : disc.secondary === 'I' ? colors.gold.muted : disc.secondary === 'S' ? 'rgba(191, 255, 0, 0.15)' : colors.violet.muted,
                    color: disc.secondary === 'D' ? colors.red : disc.secondary === 'I' ? colors.gold.DEFAULT : disc.secondary === 'S' ? colors.lime : colors.violet.DEFAULT,
                  }}
                >
                  {disc.secondary}
                </span>
              </div>
            </div>
          )}
        </div>

        {disc ? (
          <>
            {/* Progress Bars */}
            <div className="mb-6">
              {(['D', 'I', 'S', 'C'] as const).map((style, i) => (
                <DISCBar
                  key={style}
                  style={style}
                  name={discNames[style]}
                  score={disc.percentages[style]}
                  indicators={i === 0 ? disc.indicators : ''}
                  index={i}
                />
              ))}
            </div>

            {/* Communication Playbook */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl" style={{ backgroundColor: 'rgba(191, 255, 0, 0.1)' }}>
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-lg">✅</span>
                  <span className="text-sm font-semibold" style={{ color: colors.lime }}>DO THIS</span>
                </div>
                <ul className="space-y-2">
                  {disc.doList.slice(0, 4).map((item, i) => (
                    <li key={i} className="text-xs" style={{ color: colors.text.secondary }}>• {item}</li>
                  ))}
                </ul>
              </div>
              <div className="p-4 rounded-xl" style={{ backgroundColor: `${colors.red}10` }}>
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-lg">❌</span>
                  <span className="text-sm font-semibold" style={{ color: colors.red }}>DON'T DO THIS</span>
                </div>
                <ul className="space-y-2">
                  {disc.dontList.slice(0, 4).map((item, i) => (
                    <li key={i} className="text-xs" style={{ color: colors.text.secondary }}>• {item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </>
        ) : (
          <EmptyState message="No DISC data available. Enrich this contact to generate." />
        )}
      </Card>
    </motion.div>
  );
};

// =============================================================================
// COMPANY TAB
// =============================================================================
const CompanyTab: React.FC<{ content: string }> = ({ content }) => {
  const company = parseCompany(content);

  if (!company) return <EmptyState message="No company intelligence available." />;

  return (
    <motion.div variants={staggerContainer} initial="initial" animate="animate" className="space-y-6">
      {/* Company Overview */}
      <Card glow>
        <SectionTitle emoji="🏢">Company Overview</SectionTitle>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="p-3 rounded-lg" style={{ backgroundColor: colors.midnight[800] }}>
            <Label>Company</Label>
            <p className="text-sm font-medium mt-1" style={{ color: colors.text.primary }}>{company.name}</p>
          </div>
          <div className="p-3 rounded-lg" style={{ backgroundColor: colors.midnight[800] }}>
            <Label>Industry</Label>
            <p className="text-sm font-medium mt-1" style={{ color: colors.text.primary }}>{company.industry || 'N/A'}</p>
          </div>
        </div>
        
        {company.valueProposition && (
          <>
            <Label>Value Proposition</Label>
            <p className="text-sm mt-2 leading-relaxed" style={{ color: colors.text.secondary }}>
              {company.valueProposition}
            </p>
          </>
        )}
      </Card>

      {/* Products & Services */}
      {company.coreOfferings.length > 0 && (
        <Card>
          <SectionTitle emoji="📦">Products & Services</SectionTitle>
          <div className="space-y-2">
            {company.coreOfferings.map((offering, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg" style={{ backgroundColor: colors.midnight[800] }}>
                <span style={{ color: colors.gold.DEFAULT }}>•</span>
                <span className="text-sm" style={{ color: colors.text.secondary }}>{offering}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Competitive Advantages */}
      {company.advantages.length > 0 && (
        <Card>
          <SectionTitle emoji="🏆">Competitive Advantages</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {company.advantages.map((adv, i) => (
              <span
                key={i}
                className="px-3 py-2 rounded-lg text-xs font-medium"
                style={{ backgroundColor: colors.gold.muted, color: colors.gold.DEFAULT }}
              >
                {adv}
              </span>
            ))}
          </div>
        </Card>
      )}
    </motion.div>
  );
};

// =============================================================================
// PAIN POINTS TAB
// =============================================================================
const PainPointsTab: React.FC<{ content: string }> = ({ content }) => {
  const painPoints = parsePainPoints(content);

  if (painPoints.length === 0) return <EmptyState message="No pain points identified." />;

  return (
    <motion.div variants={staggerContainer} initial="initial" animate="animate" className="space-y-4">
      {painPoints.map((pain, i) => (
        <motion.div
          key={pain.number}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
        >
          <Card>
            <div className="flex items-start gap-4">
              <span
                className="w-10 h-10 rounded-xl flex items-center justify-center text-lg font-bold shrink-0"
                style={{ backgroundColor: colors.coral + '20', color: colors.coral }}
              >
                {pain.number}
              </span>
              <div>
                <h4 className="text-base font-semibold mb-2" style={{ color: colors.text.primary }}>
                  🎯 {pain.title}
                </h4>
                <p className="text-sm leading-relaxed" style={{ color: colors.text.secondary }}>
                  {pain.description}
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      ))}
    </motion.div>
  );
};

// =============================================================================
// SALES INTEL TAB
// =============================================================================
const SalesIntelTab: React.FC<{ content: string }> = ({ content }) => {
  const triggers = parseTriggerEvents(content);

  if (triggers.length === 0) return <EmptyState message="No trigger events identified." />;

  return (
    <motion.div variants={staggerContainer} initial="initial" animate="animate" className="space-y-6">
      <Card glow>
        <SectionTitle emoji="⚡">Trigger Events & Urgency Factors</SectionTitle>
        <div className="space-y-4">
          {triggers.map((trigger, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="p-4 rounded-xl border-l-4"
              style={{ backgroundColor: colors.midnight[800], borderColor: colors.gold.DEFAULT }}
            >
              <h4 className="text-sm font-semibold mb-2" style={{ color: colors.gold.DEFAULT }}>
                {trigger.title}
              </h4>
              <p className="text-sm leading-relaxed" style={{ color: colors.text.secondary }}>
                {trigger.description}
              </p>
            </motion.div>
          ))}
        </div>
      </Card>
    </motion.div>
  );
};

// =============================================================================
// OUTREACH TAB (PLACEHOLDER)
// =============================================================================
const OutreachTab: React.FC = () => (
  <Card>
    <div className="text-center py-16">
      <div className="text-5xl mb-4">✉️</div>
      <h3 className="text-xl font-bold mb-2" style={{ color: colors.text.primary }}>
        Outreach Scripts Coming Soon
      </h3>
      <p className="text-sm" style={{ color: colors.text.tertiary }}>
        AI-generated personalized outreach sequences will appear here.
      </p>
    </div>
  </Card>
);

// =============================================================================
// MAIN COMPONENT
// =============================================================================
const ContactDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [contact, setContact] = useState<Contact | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);

  // Fetch contact
  useEffect(() => {
    const fetchContact = async () => {
      try {
        const response = await fetch(`/api/contacts/${id}`);
        if (response.ok) setContact(await response.json());
      } catch (error) {
        console.error('Failed to fetch contact:', error);
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchContact();
  }, [id]);

  // Handle enrichment
  const handleEnrich = useCallback(async () => {
    if (!contact || enriching) return;
    setEnriching(true);
    try {
      const response = await fetch(`/api/contacts/${contact.id}/enrich`, { method: 'POST' });
      const result = await response.json();
      if (result.success) {
        const updated = await fetch(`/api/contacts/${contact.id}`);
        if (updated.ok) setContact(await updated.json());
      }
    } catch (error) {
      console.error('Enrichment failed:', error);
    } finally {
      setEnriching(false);
    }
  }, [contact, enriching]);

  // Content availability
  const hasContent = useMemo(() => ({
    overview: !!contact?.profile_content,
    professional: !!contact?.profile_content?.includes('Myers-Briggs'),
    company: !!contact?.profile_content?.includes('COMPANY INTELLIGENCE'),
    'pain-points': !!contact?.profile_content?.includes('Pain Point'),
    'sales-intel': !!contact?.profile_content?.includes('Trigger Events'),
    outreach: false,
  }), [contact?.profile_content]);

  // Loading
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: colors.midnight[950] }}>
        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }} style={{ color: colors.gold.DEFAULT }}>
          <Icons.RefreshCw />
        </motion.div>
      </div>
    );
  }

  // Not found
  if (!contact) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: colors.midnight[950] }}>
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4" style={{ color: colors.text.primary }}>Contact not found</h2>
          <button onClick={() => navigate(-1)} className="px-4 py-2 rounded-lg text-sm font-medium" style={{ color: colors.gold.DEFAULT }}>
            ← Go back
          </button>
        </div>
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="min-h-screen" style={{ backgroundColor: colors.midnight[950] }}>
      {/* Header */}
      <div className="sticky top-0 z-10 border-b backdrop-blur-xl" style={{ backgroundColor: `${colors.midnight[950]}ee`, borderColor: colors.midnight[600] }}>
        <div className="max-w-6xl mx-auto px-6 py-4">
          <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm font-medium transition-opacity hover:opacity-70" style={{ color: colors.text.secondary }}>
            <Icons.ArrowLeft /> Back
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Contact Header */}
        <Card className="mb-6">
          <div className="flex items-start justify-between gap-6">
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl font-bold mb-1 truncate" style={{ color: colors.text.primary }}>{contact.name}</h1>
              <p className="text-lg mb-1 truncate" style={{ color: colors.text.secondary }}>{contact.title}</p>
              <p className="truncate" style={{ color: colors.gold.DEFAULT }}>{contact.company}</p>

              {/* Contact Links */}
              <div className="flex flex-wrap gap-4 mt-6">
                {contact.email && (
                  <a href={`mailto:${contact.email}`} className="flex items-center gap-2 text-sm transition-opacity hover:opacity-70" style={{ color: colors.text.secondary }}>
                    <Icons.Mail /><span className="truncate max-w-48">{contact.email}</span>
                  </a>
                )}
                {contact.phone && (
                  <a href={`tel:${contact.phone}`} className="flex items-center gap-2 text-sm transition-opacity hover:opacity-70" style={{ color: colors.text.secondary }}>
                    <Icons.Phone />{contact.phone}
                  </a>
                )}
                {contact.linkedin_url && (
                  <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm transition-opacity hover:opacity-70" style={{ color: colors.text.secondary }}>
                    <Icons.Linkedin />Profile →
                  </a>
                )}
              </div>

              {/* Enrich Button */}
              <div className="flex items-center gap-4 mt-6">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleEnrich}
                  disabled={enriching}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all disabled:opacity-50"
                  style={{
                    backgroundColor: contact.enriched ? 'rgba(191, 255, 0, 0.15)' : colors.gold.muted,
                    color: contact.enriched ? colors.lime : colors.gold.DEFAULT,
                    border: `1px solid ${contact.enriched ? 'rgba(191, 255, 0, 0.3)' : colors.gold.DEFAULT}`,
                  }}
                >
                  {enriching ? (
                    <><motion.span animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1 }}><Icons.RefreshCw /></motion.span>Enriching...</>
                  ) : contact.enriched ? (
                    <><Icons.Check />Re-Enrich</>
                  ) : (
                    <><Icons.Sparkles />Enrich</>
                  )}
                </motion.button>
                {contact.enriched_at && (
                  <span className="text-xs" style={{ color: colors.text.tertiary }}>Last: {new Date(contact.enriched_at).toLocaleDateString()}</span>
                )}
              </div>
            </div>
            <ScoreBadge score={contact.mdcp_score || 0} size="lg" />
          </div>
        </Card>

        {/* Tab Navigation */}
        <div className="mb-6">
          <TabNav activeTab={activeTab} onTabChange={setActiveTab} hasContent={hasContent} />
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div key={activeTab} variants={tabContentVariants} initial="initial" animate="animate" exit="exit" transition={{ duration: 0.15 }}>
            {activeTab === 'overview' && <OverviewTab content={contact.profile_content || ''} contact={contact} />}
            {activeTab === 'professional' && <ProfessionalTab content={contact.profile_content || ''} />}
            {activeTab === 'company' && <CompanyTab content={contact.profile_content || ''} />}
            {activeTab === 'pain-points' && <PainPointsTab content={contact.profile_content || ''} />}
            {activeTab === 'sales-intel' && <SalesIntelTab content={contact.profile_content || ''} />}
            {activeTab === 'outreach' && <OutreachTab />}
          </motion.div>
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default ContactDetailPage;
