/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17212b",
        lake: "#126b87",
        amber: "#d9822b",
      },
    },
  },
  plugins: [],
};

