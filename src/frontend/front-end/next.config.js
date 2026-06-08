/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return [
      {
        source: '/',
        destination: '/homepage',
        permanent: false, // Consider using false during development
      },
    ];
  },
};
module.exports = nextConfig;
