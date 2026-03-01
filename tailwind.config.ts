import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#faf9f7",
        accent: "#c9a96e",
        "accent-light": "#e8d5a8",
        "sidebar-bg": "#1a1a2e",
        "text-primary": "#2d2d2d",
        "text-secondary": "#8a8a8a",
        "text-on-dark": "#e0ddd8",
        "card-bg": "#ffffff",
        border: "#e8e6e1",
        "border-light": "#f0eeea",
        "status-pending": "#f0ad4e",
        "status-approved": "#5cb85c",
        "status-rejected": "#d9534f",
        "status-executing": "#5bc0de",
        "status-completed": "#4a90d9",
        "status-new": "#9b59b6",
        "status-contacted": "#3498db",
        "status-qualified": "#2ecc71",
        "status-converted": "#27ae60",
        "status-lost": "#95a5a6",
      },
      fontFamily: {
        sans: ["Inter", "Segoe UI", "system-ui", "-apple-system", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "10px",
        sm: "6px",
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.04)",
        "card-md": "0 4px 12px rgba(0,0,0,0.06)",
      },
      spacing: {
        sidebar: "240px",
        chat: "360px",
      },
    },
  },
  plugins: [],
};

export default config;
