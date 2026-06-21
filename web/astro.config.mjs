// @ts-check
import { defineConfig } from 'astro/config';
import vercel from '@astrojs/vercel';

// Update `site` to your real domain once you have one (used for canonical URLs,
// sitemap, RSS and social share cards).
export default defineConfig({
  site: process.env.SITE_URL || 'https://paintings-explained.vercel.app',
  output: 'server',
  adapter: vercel(),
});
