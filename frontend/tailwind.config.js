/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "primary": "#256af4",
        "neon-blue": "#00f0ff",
        "neon-magenta": "#ff00ff",
        "neon-orange": "#ffaa00",
        "background-light": "#f5f6f8",
        "background-dark": "#101622",
        "surface-dark": "#1a1f2e",
        // Turbo Mode Colors
        "turbo-pink": "#f20d80",
        "turbo-red": "#ff2a2a",
        "turbo-orange": "#ff7b00",
        "turbo-bg": "#221019",
        "turbo-card": "#2a1621",
      },
      fontFamily: {
        "display": ["Space Grotesk", "sans-serif"],
        "sans": ["Inter", "sans-serif"],
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      },
      boxShadow: {
        "neon-blue": "0 0 10px rgba(0, 240, 255, 0.5), 0 0 20px rgba(0, 240, 255, 0.3)",
        "neon-magenta": "0 0 10px rgba(255, 0, 255, 0.5), 0 0 20px rgba(255, 0, 255, 0.3)",
      }
    },
  },
  plugins: [],
}
