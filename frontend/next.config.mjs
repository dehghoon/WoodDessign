// Keep the tool on the canonical website origin when cutting over, so its
// existing Supabase session is preserved. This app does not grant access.
export default {
 assetPrefix: '/_wood-assets',
 async rewrites() { return [
  {source:'/_wood-assets/_next/:path*', destination:'/_next/:path*'},
  {source:'/api/:path*',destination:'https://www.linkoteq.com/api/:path*'},
  {source:'/customer-login',destination:'https://www.linkoteq.com/customer-login'},
  {source:'/blog/login',destination:'https://www.linkoteq.com/blog/login'},
  {source:'/tools',destination:'https://www.linkoteq.com/tools'}
 ]; }
};
