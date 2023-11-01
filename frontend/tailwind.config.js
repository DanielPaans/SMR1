/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './templates/**/*.{html,js,j2}'
    ],
    theme: {
        extend: {
            colors: {
                error: '#e53731',
                warning: 'yellow',
                robot: '#60a5fa'
            },
        }
    },
    variants: {},
    plugins: [],
    safelist: [{
        pattern: /(bg|text|border)-(error|warning|robot)/
    }]
}