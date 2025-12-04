export const neonGlass = {
  dark: {
    // Backgrounds
    bg: 'bg-[#050816]',
    cardBase: 'bg-[#111928]/85',
    cardBorder: 'border-white/8',
    cardHover: 'hover:border-[#3CF2FF]/50 hover:shadow-[0_0_20px_rgba(60,242,255,0.15)]',
    
    // Glass effect
    glass: 'backdrop-blur-[18px] bg-gradient-to-br from-[#111928]/85 to-[#0F1419]/85',
    glassHover: 'hover:scale-[1.02] transition-all duration-300',
    
    // Accents
    primaryAccent: 'text-[#3CF2FF]',
    primaryAccentBg: 'bg-[#3CF2FF]',
    primaryGlow: 'shadow-[0_0_24px_rgba(60,242,255,0.4)]',
    
    secondaryAccent: 'text-[#A855FF]',
    secondaryAccentBg: 'bg-[#A855FF]',
    secondaryGlow: 'shadow-[0_0_24px_rgba(168,85,255,0.4)]',
    
    // Text
    textPrimary: 'text-[#F9FAFB]',
    textMuted: 'text-[#9CA3AF]',
    
    // Buttons
    buttonPrimary: 'bg-gradient-to-r from-[#3CF2FF] to-[#0EA5E9] text-[#050816] font-semibold rounded-full px-6 py-3 hover:shadow-[0_0_24px_rgba(60,242,255,0.5)] transition-all duration-300',
    buttonSecondary: 'bg-[#111928]/85 backdrop-blur-sm text-[#F9FAFB] border border-white/10 rounded-full px-6 py-3 hover:border-[#3CF2FF]/50 hover:shadow-[0_0_16px_rgba(60,242,255,0.2)] transition-all duration-300',
    
    // Special effects
    gradient: 'bg-gradient-to-br from-[#3CF2FF] via-[#6366F1] to-[#A855FF]',
    gradientText: 'bg-gradient-to-r from-[#3CF2FF] to-[#A855FF] bg-clip-text text-transparent',
    glow: 'shadow-[0_0_40px_rgba(60,242,255,0.3)]',
  },
  
  light: {
    // Backgrounds
    bg: 'bg-[#F5F5F9]',
    cardBase: 'bg-white',
    cardBorder: 'border-[#E5E7EB]',
    cardHover: 'hover:border-[#0EA5E9] hover:shadow-lg',
    
    // Glass effect (lighter)
    glass: 'backdrop-blur-sm bg-white/95',
    glassHover: 'hover:scale-[1.01] transition-all duration-300',
    
    // Accents
    primaryAccent: 'text-[#0EA5E9]',
    primaryAccentBg: 'bg-[#0EA5E9]',
    primaryGlow: 'shadow-[0_0_16px_rgba(14,165,233,0.3)]',
    
    secondaryAccent: 'text-[#6366F1]',
    secondaryAccentBg: 'bg-[#6366F1]',
    secondaryGlow: 'shadow-[0_0_16px_rgba(99,102,241,0.3)]',
    
    // Text
    textPrimary: 'text-[#111827]',
    textMuted: 'text-[#6B7280]',
    
    // Buttons
    buttonPrimary: 'bg-gradient-to-r from-[#0EA5E9] to-[#0284C7] text-white font-semibold rounded-full px-6 py-3 hover:shadow-lg transition-all duration-300',
    buttonSecondary: 'bg-white text-[#111827] border border-[#E5E7EB] rounded-full px-6 py-3 hover:border-[#0EA5E9] hover:shadow-md transition-all duration-300',
    
    // Special effects
    gradient: 'bg-gradient-to-br from-[#0EA5E9] via-[#6366F1] to-[#8B5CF6]',
    gradientText: 'bg-gradient-to-r from-[#0EA5E9] to-[#6366F1] bg-clip-text text-transparent',
    glow: 'shadow-lg',
  }
};
