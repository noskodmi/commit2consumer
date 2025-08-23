/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      {
        source: "/demo",
        destination: "https://www.loom.com/share/d2e729d014824b50b54f02f4cc307f8f?sid=41c34bff-581c-451f-98d3-89abe4caa4f1",
        permanent: false
      }
    ];
  }
};

module.exports = nextConfig;