/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neon: {
          cyan: '#00ffff',
          purple: '#bf00ff',
          pink: '#ff0080',
          blue: '#0080ff',
          green: '#00ff80',
        },
        dark: {
          900: '#0a0a0f',
          800: '#1a1a2e',
          700: '#16213e',
          600: '#0f3460',
        }
      },
      boxShadow: {
        'neon-cyan': '0 0 20px #00ffff, 0 0 40px #00ffff, 0 0 60px #00ffff',
        'neon-purple': '0 0 20px #bf00ff, 0 0 40px #bf00ff, 0 0 60px #bf00ff',
        'neon-pink': '0 0 20px #ff0080, 0 0 40px #ff0080, 0 0 60px #ff0080',
        'neon-blue': '0 0 20px #0080ff, 0 0 40px #0080ff, 0 0 60px #0080ff',
      },
      animation: {
        'pulse-neon': 'pulse-neon 2s ease-in-out infinite alternate',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        'pulse-neon': {
          '0%': { boxShadow: '0 0 20px #00ffff, 0 0 40px #00ffff' },
          '100%': { boxShadow: '0 0 30px #00ffff, 0 0 60px #00ffff, 0 0 80px #00ffff' }
        },
        'glow': {
          '0%': { textShadow: '0 0 10px #00ffff, 0 0 20px #00ffff' },
          '100%': { textShadow: '0 0 20px #00ffff, 0 0 30px #00ffff, 0 0 40px #00ffff' }
        }
      }
    },
  },
  plugins: [],
}