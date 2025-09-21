module.exports = {
  content: [
    './templates/**/*.html',  // ← make sure this is set properly
    './**/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('tailwind-scrollbar'),
  ],
}
