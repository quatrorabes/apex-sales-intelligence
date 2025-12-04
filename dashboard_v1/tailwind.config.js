/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Warm Midnight Background Palette
        midnight: {
          950: '#0A0A0A',  // Page background
          900: '#141414',  // Cards, panels
          800: '#1C1C1C',  // Elevated, hover
          700: '#262626',  // Secondary elevations
          600: '#2A2A2A',  // Borders
          500: '#3D3D3D',  // Hover borders
        },
        
        // Primary Accent — Gold (Hot Scores, CTAs)
        gold: {
          DEFAULT: '#E5B84C',
          hover: '#D4A853',
          muted: 'rgba(229, 184, 76, 0.15)',
          glow: 'rgba(229, 184, 76, 0.25)',
        },
        
        // Secondary Accent — Deep Blue (AI Elements)
        blue: {
          DEFAULT: '#3B82F6',  // Vibrant deep blue
          muted: 'rgba(59, 130, 246, 0.15)',
        },
        
        // Legacy violet alias (for backwards compatibility)
        violet: {
          DEFAULT: '#3B82F6',
          muted: 'rgba(59, 130, 246, 0.15)',
        },
        
        // Status Colors
        lime: '#BFFF00',      // Success, positive
        coral: '#F97316',     // Warning, warm scores
        red: '#EF4444',       // Urgent, errors
        magenta: '#E879F9',   // Special highlights
        
        // Text Hierarchy
        text: {
          primary: '#FAFAFA',
          secondary: '#A3A3A3',
          tertiary: '#737373',
        },
      },
      
      boxShadow: {
        'gold-glow': '0 0 20px rgba(229, 184, 76, 0.15)',
        'blue-glow': '0 0 20px rgba(59, 130, 246, 0.2)',
        'card-hover': '0 8px 24px rgba(0, 0, 0, 0.4)',
        'brutal': '4px 4px 0px rgba(0, 0, 0, 0.8)',
      },
      
      borderRadius: {
        'card': '16px',
        'card-sm': '12px',
      },
      
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      
      animation: {
        'breathing': 'breathing 3s ease-in-out infinite',
        'score-tick': 'scoreTick 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'card-enter': 'cardEnter 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
      
      keyframes: {
        breathing: {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '1' },
        },
        scoreTick: {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.1)' },
          '100%': { transform: 'scale(1)' },
        },
        cardEnter: {
          '0%': { 
            opacity: '0',
            transform: 'translateY(10px) scale(0.95)'
          },
          '100%': { 
            opacity: '1',
            transform: 'translateY(0) scale(1)'
          },
        },
      },
      
      transitionTimingFunction: {
        'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
    },
  },
  plugins: [],
}