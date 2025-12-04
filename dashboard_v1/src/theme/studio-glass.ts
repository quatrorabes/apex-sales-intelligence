export const studioGlass = {
  dark: {
    // Backgrounds
    bg: 'bg-[#050816]',
    surface: 'bg-[#0B1120]',
    surfaceHover: 'hover:bg-gradient-to-br hover:from-[#0B1120] hover:to-[#020617]',
    
    // Cards - Subtle glass
    card: 'bg-[#0B1120] backdrop-blur-sm',
    cardBorder: 'border-[#94A3B8]/35',
    cardShadow: 'shadow-[0_18px_45px_rgba(15,23,42,0.6)]',
    cardHover: 'hover:shadow-[0_20px_50px_rgba(15,23,42,0.7)] hover:border-[#94A3B8]/50 transition-all duration-200',
    
    // Glass overlay (optional)
    glass: 'backdrop-blur-[8px] bg-[#0F1729]/75',
    
    // Accents - Toned down
    primaryAccent: 'text-[#22D3EE]',
    primaryAccentBg: 'bg-[#22D3EE]',
    secondaryAccent: 'text-[#6366F1]',
    secondaryAccentBg: 'bg-[#6366F1]',
    
    // Neutrals
    neutral: 'bg-[#1E293B]',
    neutralBorder: 'border-[#1E293B]',
    
    // Text
    textPrimary: 'text-[#F9FAFB]',
    textSecondary: 'text-[#CBD5E1]',
    textMuted: 'text-[#64748B]',
    
    // Status
    success: 'text-[#22C55E]',
    successBg: 'bg-[#22C55E]/10',
    warning: 'text-[#EAB308]',
    warningBg: 'bg-[#EAB308]/10',
    
    // Buttons
    btnPrimary: 'bg-[#22D3EE] text-[#050816] hover:bg-[#06B6D4] font-semibold rounded-lg px-4 py-2 transition-all duration-150',
    btnSecondary: 'border border-[#22D3EE] text-[#22D3EE] bg-transparent hover:bg-[#22D3EE]/10 rounded-lg px-4 py-2 transition-all duration-150',
    
    // Chips
    chip: 'bg-[#94A3B8]/12 text-[#CBD5E1] px-3 py-1 rounded-full text-xs',
    chipActive: 'bg-[#22D3EE] text-[#050816] px-3 py-1 rounded-full text-xs font-medium',
    
    // Focus ring
    focusRing: 'focus:outline-none focus:ring-2 focus:ring-[#22D3EE] focus:ring-offset-2 focus:ring-offset-[#050816]',
    
    // Table
    tableRowAlt: 'bg-[#0F1729]/60',
    tableRowHover: 'hover:bg-[#1E293B]/50',
  },
  
  light: {
    // Backgrounds
    bg: 'bg-[#F4F5FB]',
    surface: 'bg-white',
    surfaceHover: 'hover:bg-gray-50',
    
    // Cards
    card: 'bg-white',
    cardBorder: 'border-[#E5E7EB]',
    cardShadow: 'shadow-sm',
    cardHover: 'hover:shadow-md hover:border-[#D1D5DB] transition-all duration-200',
    
    // Glass overlay
    glass: 'backdrop-blur-sm bg-white/95',
    
    // Accents
    primaryAccent: 'text-[#0EA5E9]',
    primaryAccentBg: 'bg-[#0EA5E9]',
    secondaryAccent: 'text-[#4F46E5]',
    secondaryAccentBg: 'bg-[#4F46E5]',
    
    // Neutrals
    neutral: 'bg-[#F3F4F6]',
    neutralBorder: 'border-[#E5E7EB]',
    
    // Text
    textPrimary: 'text-[#111827]',
    textSecondary: 'text-[#4B5563]',
    textMuted: 'text-[#6B7280]',
    
    // Status
    success: 'text-[#16A34A]',
    successBg: 'bg-[#22C55E]/10',
    warning: 'text-[#CA8A04]',
    warningBg: 'bg-[#EAB308]/10',
    
    // Buttons
    btnPrimary: 'bg-[#0EA5E9] text-white hover:bg-[#0284C7] font-semibold rounded-lg px-4 py-2 transition-all duration-150',
    btnSecondary: 'border border-[#0EA5E9] text-[#0EA5E9] bg-transparent hover:bg-[#0EA5E9]/10 rounded-lg px-4 py-2 transition-all duration-150',
    
    // Chips
    chip: 'bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-xs',
    chipActive: 'bg-[#0EA5E9] text-white px-3 py-1 rounded-full text-xs font-medium',
    
    // Focus ring
    focusRing: 'focus:outline-none focus:ring-2 focus:ring-[#0EA5E9] focus:ring-offset-2 focus:ring-offset-white',
    
    // Table
    tableRowAlt: 'bg-gray-50',
    tableRowHover: 'hover:bg-gray-100',
  }
};
