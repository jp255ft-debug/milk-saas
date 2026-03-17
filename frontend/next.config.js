/** @type {import('next').NextConfig} */
const nextConfig = {
  // serverActions está habilitado por padrão no Next.js 16
};

const withNextIntl = require('next-intl/plugin')();

module.exports = withNextIntl(nextConfig);
