import type { APIRoute } from 'astro';
import { listPaintings } from '../lib/queries';

const escapeXml = (s: string) =>
  s.replace(/[<>&'"]/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', "'": '&apos;', '"': '&quot;' }[c]!));

export const GET: APIRoute = async ({ site }) => {
  const base = (site?.href ?? 'https://paintings-explained.vercel.app').replace(/\/$/, '');
  const paintings = await listPaintings();

  const items = paintings
    .map((p) => {
      const url = `${base}/paintings/${p.slug}`;
      return `    <item>
      <title>${escapeXml(p.title)}</title>
      <link>${url}</link>
      <guid>${url}</guid>
      ${p.summary ? `<description>${escapeXml(p.summary)}</description>` : ''}
    </item>`;
    })
    .join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Paintings Explained</title>
    <link>${base}</link>
    <description>The hidden details in the world's most-watched paintings.</description>
    <language>en</language>
${items}
  </channel>
</rss>`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8', 'Cache-Control': 'public, s-maxage=600' },
  });
};
