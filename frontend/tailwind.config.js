/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#030d1a',
          900: '#071428',
          800: '#0d1f3e',
          700: '#112b54',
          600: '#16376a',
          500: '#1d4ed8',
        },
        frost: {
          DEFAULT: '#ffffff',
          90:  'rgba(255,255,255,0.90)',
          70:  'rgba(255,255,255,0.70)',
          50:  'rgba(255,255,255,0.50)',
          20:  'rgba(255,255,255,0.20)',
          10:  'rgba(255,255,255,0.10)',
        },
        sky: {
          400: '#60a5fa',
          300: '#93c5fd',
          200: '#bfdbfe',
        },
        warning: '#f59e0b',
        danger:  '#ef4444',
        success: '#10b981',
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
