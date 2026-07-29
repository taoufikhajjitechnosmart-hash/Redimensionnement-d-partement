/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@sim/engine', '@sim/data', '@sim/domain'],
  experimental: { typedRoutes: true },
};

export default nextConfig;
