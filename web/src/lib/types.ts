export interface Artist {
  id: string;
  slug: string;
  name: string;
  bio: string | null;
  nationality: string | null;
  birth_year: number | null;
  death_year: number | null;
}

export interface Hotspot {
  id: string;
  x: number;
  y: number;
  title: string;
  detail: string;
  ordinal: number;
}

export interface Tag {
  slug: string;
  name: string;
}

export interface Painting {
  id: string;
  slug: string;
  title: string;
  year: string | null;
  year_sort: number | null;
  movement: string | null;
  museum: string | null;
  medium: string | null;
  image_url: string;
  iiif_url: string | null;
  thumb_url: string | null;
  width: number | null;
  height: number | null;
  source: string;
  credit: string | null;
  license: string;
  summary: string | null;
  why_watch: string | null;
  body: string | null;
  featured: boolean;
  artist: Artist | null;
  hotspots: Hotspot[];
  tags: Tag[];
}

export interface Facet {
  value: string;
  label: string;
  count: number;
}
