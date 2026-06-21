-- Paintings Explained — core schema
-- Apply in the Supabase SQL editor (or via the Supabase CLI). Idempotent-ish:
-- uses "create table if not exists" so re-running is safe.

create extension if not exists pgcrypto;   -- gen_random_uuid()
create extension if not exists pg_trgm;     -- fast ILIKE search

-- ---------------------------------------------------------------------------
-- artists
-- ---------------------------------------------------------------------------
create table if not exists artists (
  id            uuid primary key default gen_random_uuid(),
  slug          text unique not null,
  name          text not null,
  bio           text,
  birth_year    int,
  death_year    int,
  nationality   text,
  created_at    timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- paintings
-- ---------------------------------------------------------------------------
create table if not exists paintings (
  id            uuid primary key default gen_random_uuid(),
  slug          text unique not null,
  title         text not null,
  artist_id     uuid references artists(id) on delete set null,
  year          text,                       -- display form, e.g. "c. 1533"
  year_sort     int,                         -- numeric year for sorting / era filter
  movement      text,                        -- e.g. Baroque, Northern Renaissance
  museum        text,
  medium        text,
  image_url     text not null,               -- high-res JPEG
  iiif_url      text,                         -- IIIF image base (Art Institute) for deep zoom
  thumb_url     text,
  width         int,
  height        int,
  source        text not null default 'manual' check (source in ('met','artic','manual')),
  object_id     text not null,               -- museum's object id (or a manual id)
  license       text not null default 'CC0',
  credit        text,
  summary       text,                        -- one-line hook
  why_watch     text,                        -- "why people stare for hours"
  body          text,                        -- full explanation (markdown)
  featured      boolean not null default false,
  published     boolean not null default false,
  view_count    int not null default 0,
  published_at  timestamptz,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  unique (source, object_id)
);

create index if not exists paintings_published_idx on paintings (published);
create index if not exists paintings_featured_idx  on paintings (featured);
create index if not exists paintings_artist_idx    on paintings (artist_id);
create index if not exists paintings_movement_idx  on paintings (movement);
create index if not exists paintings_year_idx      on paintings (year_sort);
create index if not exists paintings_title_trgm_idx on paintings using gin (title gin_trgm_ops);

-- ---------------------------------------------------------------------------
-- hotspots — the clickable "hidden detail" markers (x/y are % of image, 0–100)
-- ---------------------------------------------------------------------------
create table if not exists hotspots (
  id            uuid primary key default gen_random_uuid(),
  painting_id   uuid not null references paintings(id) on delete cascade,
  x             numeric not null check (x >= 0 and x <= 100),
  y             numeric not null check (y >= 0 and y <= 100),
  title         text not null,
  detail        text not null,
  ordinal       int not null default 0,
  created_at    timestamptz not null default now()
);
create index if not exists hotspots_painting_idx on hotspots (painting_id);

-- ---------------------------------------------------------------------------
-- tags + many-to-many (themes / browse facets)
-- ---------------------------------------------------------------------------
create table if not exists tags (
  id            uuid primary key default gen_random_uuid(),
  slug          text unique not null,
  name          text not null,
  description   text
);
create table if not exists painting_tags (
  painting_id   uuid not null references paintings(id) on delete cascade,
  tag_id        uuid not null references tags(id) on delete cascade,
  primary key (painting_id, tag_id)
);

-- ---------------------------------------------------------------------------
-- collections (Phase 2 themed sets — defined now so the schema is stable)
-- ---------------------------------------------------------------------------
create table if not exists collections (
  id                 uuid primary key default gen_random_uuid(),
  slug               text unique not null,
  title              text not null,
  description        text,
  cover_painting_id  uuid references paintings(id) on delete set null,
  published          boolean not null default false,
  created_at         timestamptz not null default now()
);
create table if not exists collection_paintings (
  collection_id  uuid not null references collections(id) on delete cascade,
  painting_id    uuid not null references paintings(id) on delete cascade,
  ordinal        int not null default 0,
  primary key (collection_id, painting_id)
);

-- ---------------------------------------------------------------------------
-- keep updated_at fresh on paintings
-- ---------------------------------------------------------------------------
create or replace function set_updated_at() returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists paintings_set_updated_at on paintings;
create trigger paintings_set_updated_at
  before update on paintings
  for each row execute function set_updated_at();
