/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@sim/engine', '@sim/data', '@sim/domain'],
  typedRoutes: true,
};

export default nextConfig;
