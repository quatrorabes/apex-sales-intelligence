/**
 * APEX Design System — Component Utility Classes
 * Warm Midnight Theme v1.0
 */

export const cardClasses = {
  base: `
    bg-midnight-900 
    border border-midnight-600 
    rounded-card 
    transition-all duration-200
    hover:border-midnight-500 
    hover:shadow-card-hover
  `,
  
  elevated: `
    bg-midnight-800 
    border border-midnight-600 
    rounded-card
  `,
  
  interactive: `
    bg-midnight-900 
    border border-midnight-600 
    rounded-card 
    transition-all duration-200
    hover:translate-x-1
    hover:shadow-gold-glow
    active:scale-[0.99]
    cursor-pointer
  `,
  
  focus: `
    ring-2 ring-gold ring-opacity-50
    border-gold
  `,
};

export const buttonClasses = {
  primary: `
    bg-gradient-to-r from-gold to-gold-hover
    text-midnight-950 
    font-semibold
    px-6 py-3 
    rounded-xl
    transition-all duration-200
    hover:shadow-gold-glow
    active:scale-[0.97]
  `,
  
  secondary: `
    bg-transparent
    border-2 border-midnight-600
    text-text-primary
    font-semibold
    px-6 py-3
    rounded-xl
    transition-all duration-200
    hover:border-gold
    hover:text-gold
    active:scale-[0.97]
  `,
  
  action: `
    bg-midnight-800
    text-text-secondary
    px-4 py-2
    rounded-lg
    text-sm
    transition-all duration-200
    hover:bg-gold-muted
    hover:text-gold
    active:scale-[0.97]
  `,
};

export const scoreClasses = {
  hot: `
    text-gold 
    font-bold 
  `,
  
  warm: `
    text-coral 
    font-semibold
  `,
  
  cold: `
    text-text-tertiary 
    font-medium
  `,
};

export const accentBorders = {
  hot: 'border-l-4 border-gold',
  warm: 'border-l-4 border-coral',
  urgent: 'border-l-4 border-red',
  ai: 'border-l-4 border-violet',
};

// Helper function for score styling
export const getScoreClass = (score: number): string => {
  if (score >= 85) return scoreClasses.hot;
  if (score >= 60) return scoreClasses.warm;
  return scoreClasses.cold;
};

// Helper function for accent border
export const getAccentBorder = (score: number, isAI?: boolean): string => {
  if (isAI) return accentBorders.ai;
  if (score >= 85) return accentBorders.hot;
  if (score >= 60) return accentBorders.warm;
  return accentBorders.urgent;
};