import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const page=readFileSync('app/tools/wood-design/page.tsx','utf8');
for (const field of ['title','description','canonical','openGraph','robots']) assert.ok(page.includes(field),field);
assert.ok(page.includes('https://www.linkoteq.com/tools/wood-design'));
assert.ok(/Beta|Unverified/.test(page));
for(const path of ['app/robots.ts','app/sitemap.ts'])assert.ok(readFileSync(path,'utf8').includes('https://www.linkoteq.com'));
console.log('Standalone landing-page SEO checks passed');
