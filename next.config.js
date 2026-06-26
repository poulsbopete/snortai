/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    instrumentationHook: true,
  },
  reactStrictMode: true,
  // API routes require serverless functions, not static export
  // Don't set output: 'export' - that would disable API routes
}

module.exports = nextConfig
