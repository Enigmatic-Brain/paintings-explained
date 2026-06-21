import { supabase } from './supabase';
import type { Artist, Facet, Painting } from './types';

const SELECT = `
  id, slug, title, year, year_sort, movement, museum, medium,
  image_url, iiif_url, thumb_url, width, height, source, credit, license,
  summary, why_watch, body, featured,
  artist:artists(id, slug, name, bio, nationality, birth_year, death_year),
  hotspots(id, x, y, title, detail, ordinal),
  painting_tags(tags(slug, name))
`;

function mapPainting(row: any): Painting {
  return {
    ...row,
    artist: row.artist ?? null,
    hotspots: (row.hotspots ?? []).sort((a: any, b: any) => a.ordinal - b.ordinal),
    tags: (row.painting_tags ?? []).map((pt: any) => pt.tags).filter(Boolean),
  } as Painting;
}

export interface ListFilters {
  movement?: string;
  artist?: string;
  q?: string;
}

export async function listPaintings(filters: ListFilters = {}): Promise<Painting[]> {
  let query = supabase
    .from('paintings')
    .select(SELECT)
    .eq('published', true)
    .order('featured', { ascending: false })
    .order('year_sort', { ascending: true, nullsFirst: false });

  if (filters.movement) query = query.eq('movement', filters.movement);
  if (filters.q) query = query.ilike('title', `%${filters.q}%`);

  const { data, error } = await query;
  if (error) throw error;
  let rows = (data ?? []).map(mapPainting);

  // Artist filter is by slug, which lives on the joined row — filter in memory
  // (the catalogue is small; this keeps the query simple).
  if (filters.artist) rows = rows.filter((p) => p.artist?.slug === filters.artist);
  return rows;
}

export async function getPainting(slug: string): Promise<Painting | null> {
  const { data, error } = await supabase
    .from('paintings')
    .select(SELECT)
    .eq('slug', slug)
    .eq('published', true)
    .maybeSingle();
  if (error) throw error;
  return data ? mapPainting(data) : null;
}

export async function getFeatured(limit = 6): Promise<Painting[]> {
  const all = await listPaintings();
  const featured = all.filter((p) => p.featured);
  return (featured.length ? featured : all).slice(0, limit);
}

/** Deterministic "Painting of the Day": same pick for everyone, rotates daily. */
export async function getPaintingOfTheDay(): Promise<Painting | null> {
  const all = await listPaintings();
  if (!all.length) return null;
  const epochDay = Math.floor(Date.now() / 86_400_000);
  return all[epochDay % all.length];
}

export async function getRelated(painting: Painting, limit = 3): Promise<Painting[]> {
  const all = await listPaintings();
  const scored = all
    .filter((p) => p.id !== painting.id)
    .map((p) => {
      let score = 0;
      if (p.artist?.slug && p.artist.slug === painting.artist?.slug) score += 2;
      if (p.movement && p.movement === painting.movement) score += 1;
      return { p, score };
    })
    .sort((a, b) => b.score - a.score);
  return scored.slice(0, limit).map((s) => s.p);
}

export async function getMovementFacets(): Promise<Facet[]> {
  const all = await listPaintings();
  return facetsFrom(all.map((p) => p.movement).filter(Boolean) as string[]);
}

export async function getArtistFacets(): Promise<Facet[]> {
  const all = await listPaintings();
  const counts = new Map<string, Facet>();
  for (const p of all) {
    if (!p.artist) continue;
    const f = counts.get(p.artist.slug) ?? { value: p.artist.slug, label: p.artist.name, count: 0 };
    f.count += 1;
    counts.set(p.artist.slug, f);
  }
  return [...counts.values()].sort((a, b) => a.label.localeCompare(b.label));
}

export async function getArtistBySlug(slug: string): Promise<Artist | null> {
  const { data, error } = await supabase.from('artists').select('*').eq('slug', slug).maybeSingle();
  if (error) throw error;
  return (data as Artist) ?? null;
}

function facetsFrom(values: string[]): Facet[] {
  const counts = new Map<string, number>();
  for (const v of values) counts.set(v, (counts.get(v) ?? 0) + 1);
  return [...counts.entries()]
    .map(([value, count]) => ({ value, label: value, count }))
    .sort((a, b) => a.label.localeCompare(b.label));
}

/** Slugify a movement name for use in URLs (movements aren't stored with slugs). */
export function movementSlug(movement: string): string {
  return movement.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}
