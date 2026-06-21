import type { APIRoute } from 'astro';
import { listPaintings, getArtistFacets, getMovementFacets, movementSlug } from '../lib/queries';

export const GET: APIRoute = async ({ site }) => {
  const base = (site?.href ?? 'https://paintings-explained.vercel.app').replace(/\/$/, '');
  const [paintings, artists, movements] = await Promise.all([
    listPaintings(),
    getArtistFacets(),
    getMovementFacets(),
  ]);

  const urls = [
    `${base}/`,
    `${base}/paintings`,
    `${base}/about`,
    ...paintings.map((p) => `${base}/paintings/${p.slug}`),
    ...artists.map((a) => `${base}/artists/${a.value}`),
    ...movements.map((m) => `${base}/movements/${movementSlug(m.value)}`),
  ];

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map((u) => `  <url><loc>${u}</loc></url>`).join('\n')}
</urlset>`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8', 'Cache-Control': 'public, s-maxage=600' },
  });
};
