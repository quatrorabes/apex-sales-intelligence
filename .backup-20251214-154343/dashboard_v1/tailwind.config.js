/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          '"SF Pro Text"',
          'Inter',
          'sans-serif',
        ],
      },
      colors: {
        bg: {
          app: '#050608',
          sidebar: '#111319',
          surface: '#151821',
          surfaceAlt: '#1a1e28',
          surfaceElevated: '#1e2230',
        },
        textc: {
          primary: '#F5F7FB',
          secondary: '#A2A8B8',
          muted: '#6B7180',
          onAccent: '#F9FBFF',
        },
        accent: {
          blue: '#4B8AFF',
          indigo: '#5865F2',
          orange: '#FF9A4A',
          pink: '#F27AD6',
          violet: '#A56BFF',
          danger: '#FF6A4F',
          info: '#3B82F6',
        },
        borderc: {
          subtle: 'rgba(255,255,255,0.04)',
          medium: 'rgba(255,255,255,0.08)',
          strong: 'rgba(255,255,255,0.12)',
        },
      },
      borderRadius: {
        xs: '0.5rem',
        sm: '0.75rem',
        md: '1rem',
        lg: '1.125rem',
      },
      boxShadow: {
        card: '0 6px 18px rgba(0,0,0,0.55)',
        panel: '0 12px 30px rgba(0,0,0,0.6)',
        elevated: '0 22px 60px rgba(0,0,0,0.85)',
        glowOrange: '0 0 24px rgba(255,154,74,0.45)',
        glowBlue: '0 0 24px rgba(75,138,255,0.4)',
      },
      backgroundImage: {
        'card-subtle': 'linear-gradient(180deg, rgba(255,255,255,0.02), rgba(4,5,7,0.92))',
      },
    },
  },
  plugins: [],
};
