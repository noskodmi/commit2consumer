/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      {
        source: "/demo",
        destination: "YOUR_LOOM_SHARE_URL",
        permanent: false
      }
    ];
  }
};

module.exports = nextConfig;