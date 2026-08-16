/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        orange: {
          '50': '#fef8f3',
          '100': '#fef0e8',
          '200': '#fcdcc6',
          '300': '#f9c9a3',
          '400': '#f5a55e',
          '500': '#f0812f',
          '600': '#ea580c',
          '700': '#b85c2c',
          '800': '#934a2b',
          '900': '#743d25',
        },
      },
    },
  },
  plugins: [],
}
