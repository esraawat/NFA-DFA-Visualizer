/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', 'Consolas', 'monospace'],
      },
      colors: {
        canvas:  '#0d1117',
        surface: '#161b22',
        border:  '#30363d',
        muted:   '#8b949e',
        accent:  '#7c3aed',
        accept:  '#16a34a',
        reject:  '#dc2626',
        active:  '#f59e0b',
      },
    },
  },
  plugins: [],
}
