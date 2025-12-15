const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx,js,jsx}'],
  theme: {
    extend: {
      colors: {
        graphite: { 950: '#050B0F', 900: '#0B1220' },
        slatepanel: { 900: '#111827', 800: '#1F2937', 700: '#374151' },
        teal: { 500: '#14B8A6', 600: '#0D9488' },
        amber: { 500: '#F59E0B', 600: '#D97706' },
        ink: { 50: '#F9FAFB', 900: '#111827' },
        steel: { 100: '#F3F4F6', 400: '#9CA3AF' },
      },
      borderRadius: { card: '4px' },
      boxShadow: { 'card-soft': '0 4px 16px rgba(0,0,0,0.25)' },
      fontFamily: {
        sans: ['system-ui', 'Inter', ...defaultTheme.fontFamily.sans],
        mono: ['ui-monospace', 'SFMono-Regular', ...defaultTheme.fontFamily.mono],
      },
    },
  },
  plugins: [],
};
