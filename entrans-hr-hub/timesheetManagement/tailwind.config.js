/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,ts}",
],
  theme: {
    extend: {
       colors: {
        'primary': '#1F3A5F',
        'primary-hover': '#14263f',
        'secondary': '#F5F5F5',
        'accent': '#E2A512',
        'success': '#10B981',
        'error': '#EF4444',
        'warning': '#F59E0B',
        'gray-light': '#F5F5F5',
        'gray-border': '#E5E7EB',
      },
      fontFamily: {
        sans: ['Inter', 'Poppins', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

