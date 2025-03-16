/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: true,
  },
  // 确保路由正确解析
  async rewrites() {
    return [
      {
        source: '/course-planning',
        destination: '/course-planning',
      },
      {
        source: '/career-goals',
        destination: '/career-goals',
      },
      {
        source: '/feedback',
        destination: '/feedback',
      },
    ];
  },
};

module.exports = nextConfig; 