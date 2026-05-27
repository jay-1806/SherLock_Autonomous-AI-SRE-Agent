/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_USE_DEMO: process.env.NEXT_PUBLIC_USE_DEMO || 'true',
  },
}

module.exports = nextConfig
