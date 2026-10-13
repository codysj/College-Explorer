import type { NextConfig } from "next";

// ponytail: a CSP without script-src. Next injects inline bootstrap scripts, so a script
// policy needs per-request nonces from middleware; these directives block framing,
// plugins, and base/form hijacking without that machinery. Add nonces if the app ever
// renders third-party or user-authored HTML.
const securityHeaders = [
  { key: "Content-Security-Policy", value: "frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
];

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "standalone",
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
};

export default nextConfig;
