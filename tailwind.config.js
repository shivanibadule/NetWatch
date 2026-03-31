/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'nw-bg': 'var(--nw-bg)',
        'nw-bg-alt': 'var(--nw-bg-alt)',
        'nw-card': 'var(--nw-card)',
        'nw-border': 'var(--nw-border)',
        'nw-accent': 'var(--nw-accent)',
        'nw-accent2': 'var(--nw-accent2)',
        'nw-success': 'var(--nw-success)',
        'nw-warning': 'var(--nw-warning)',
        'nw-danger': 'var(--nw-danger)',
        'nw-text': 'var(--nw-text)',
        'nw-muted': 'var(--nw-muted)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(59, 130, 246, 0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(59, 130, 246, 0.6)' },
        },
      },
    },
  },
  plugins: [],
}
